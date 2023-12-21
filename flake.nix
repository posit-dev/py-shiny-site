{
  description = "py-shiny-site";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.11";
    # Pin to this release of nixpkgs to use Quarto 1.3. (This is currently the same as
    # nixpkgs above but they may change independently in the future.)
    nixpkgs-quarto.url = "github:NixOS/nixpkgs/nixos-23.11";
  };

  outputs = { self, nixpkgs, nixpkgs-quarto }:
    let
      allSystems =
        [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];

      # Helper to provide system-specific attributes
      forAllSystems = f:
        nixpkgs.lib.genAttrs allSystems (system:
          f rec {
            quartoOverlay = final: prev: {
              # Modifications to Quarto from:
              # https://github.com/quarto-dev/quarto-cli/blob/fee994d5476fd1a23c37b8a700c027cdb4267688/src/resources/schema/cell-attributes.yml
              quarto = (prev.quarto.overrideAttrs (oldAttrs: {
                # The original preFixup also set QUARTO_R and QUARTO_PYTHON. Setting the
                # latter seems to make Quarto ignore virtualenvs. I think that with
                # those vars set, Quarto would always use those copies of R and Python
                # instead of the versions of R and Python we've installed ourselves.
                preFixup = ''
                  wrapProgram $out/bin/quarto \
                    --prefix PATH : ${prev.lib.makeBinPath [ prev.deno ]} \
                    --prefix QUARTO_DENO : ${prev.deno}/bin/deno \
                    --prefix QUARTO_PANDOC : ${prev.pandoc}/bin/pandoc \
                    --prefix QUARTO_ESBUILD : ${prev.esbuild}/bin/esbuild \
                    --prefix QUARTO_DART_SASS : ${prev.dart-sass}/bin/dart-sass \
                '';

              })) //
                # Additional modifications to quarto, for Mac only.
                (nixpkgs.lib.attrsets.optionalAttrs pkgs.stdenv.isDarwin {
                  # The previous recipe always fetched the Linux build. On Mac, fetch the
                  # Mac build.
                  src = prev.fetchurl {
                    url =
                      "https://github.com/quarto-dev/quarto-cli/releases/download/v${prev.oldAttrs.version}/quarto-${prev.oldAttrs.version}-macos.tar.gz";
                    sha256 =
                      "sha256-w9pqJr1Y8H4Yqqd+YhVzKGtKEntz4CP4nqeVZ6MKoFw=";
                  };

                  # The Linux tarball has /quarto-x.xx.x/, which contains a bin/ and
                  # share/ directory, but the Mac tarball just has /bin/ and /share/. This
                  # causes the unpackPhase to fail -- Nix complains about multiple files
                  # in the directory. To work around this, we set sourceRoot to "." and
                  # then after unpacking, create a directory quarto/, and move bin/ and
                  # share/ into it.
                  sourceRoot = ".";

                  postUnpack = ''
                    mkdir quarto
                    mv bin share quarto
                    sourceRoot=quarto
                  '';

                });
            };

            pkgs = import nixpkgs { inherit system; };

            pkgs-quarto = import nixpkgs-quarto {
              inherit system;
              overlays = [ quartoOverlay ];
            };

            inherit system;
          });

    in {
      # Development environment output
      devShells = forAllSystems ({ pkgs, pkgs-quarto, system, ... }: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            git
            which
            rsync
            (with rPackages; [ R rmarkdown reticulate ])
            python311
            pkgs-quarto.quarto
            # Quarto uses `rmarkdown::pandoc_available()` when running rmd files, which
            # in turn calls `find_pandoc()` -> `find_program("pandoc")`, and on Linux,
            # this calls `Sys.which("pandoc")` (it does something a bit different on
            # Mac). This means that pandoc needs to be in the PATH. So we'll explicitly
            # add it here, making sure that that it comes from pkgs-quarto, so it's
            # the same copy that quarto would find anyway.
            # https://github.com/quarto-dev/quarto-cli/blob/fee994d5/src/resources/rmd/rmd.R#L219C12-L228
            pkgs-quarto.pandoc
            sysctl # Needed by Quarto to detect system
          ];
          # Need to set LD_LIBRARY_PATH to load some Python packages on Linux (like zmq,
          # which is used by jupyter_client).
          # https://discourse.nixos.org/t/how-to-solve-libstdc-not-found-in-shell-nix/25458
          #
          # For some reason, the rmarkdown package on Linux requires HOME to be set when
          # running pandoc. When running with `nix develop -i`, there is no HOME;
          # however, `~` will expand to the user's home directory, so we set HOME to ~.
          # https://github.com/rstudio/rmarkdown/issues/31#issuecomment-41218736
          shellHook = pkgs.lib.strings.optionalString (!pkgs.stdenv.isDarwin) ''
            export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib/
            if [ -z "$HOME" ]; then
              export HOME=~
            fi
          '';
        };
      });
    };
}

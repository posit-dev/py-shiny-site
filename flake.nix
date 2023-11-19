{
  description = "py-shiny-site";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.05";
    # Use unstable channel for recent version of Quarto
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs, nixpkgs-unstable }:
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
              quarto = prev.quarto.overrideAttrs (oldAttrs: {
                # The previous recipe always fetched the Linux build.
                src = prev.fetchurl {
                  url =
                    "https://github.com/quarto-dev/quarto-cli/releases/download/v${oldAttrs.version}/quarto-${oldAttrs.version}-macos.tar.gz";
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

                # The previous installPhase script removed bin/tools, which caused deno
                # to fail to start.
                installPhase = ''
                  runHook preInstall

                  mkdir -p $out/bin $out/share

                  # rm -r bin/tools

                  mv bin/* $out/bin
                  mv share/* $out/share

                  runHook postInstall
                '';

                # The original preFixup also set QUARTO_R and QUARTO_PYTHON. Setting the
                # latter seems to make Quarto ignore virtualenvs. I think that with
                # these set, Quarto would always use those copies of R and Python
                # instead of the versions of R and Python we've installed ourselves.
                preFixup = ''
                  wrapProgram $out/bin/quarto \
                    --prefix PATH : ${prev.lib.makeBinPath [ prev.deno ]} \
                    --prefix QUARTO_PANDOC : ${prev.pandoc}/bin/pandoc \
                    --prefix QUARTO_ESBUILD : ${prev.esbuild}/bin/esbuild \
                    --prefix QUARTO_DART_SASS : ${prev.dart-sass}/bin/dart-sass \
                '';

              });
            };

            pkgs = import nixpkgs {
              inherit system;

            };
            # pkgs = (pkgs1.extend overlay1).extend overlay2;
            pkgs-unstable = import nixpkgs-unstable {
              inherit system;
              overlays = [ quartoOverlay ];
            };
            inherit system;
          });

    in {
      # Development environment output
      devShells = forAllSystems ({ pkgs, pkgs-unstable, system, ... }: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            git
            which
            rsync
            (with rPackages; [ rmarkdown R ])
            (python311.withPackages (ps: with ps; [ pip virtualenv ]))
            pkgs-unstable.quarto
            sysctl # Needed by Quarto to detect system
          ];
        };
      });
    };
}

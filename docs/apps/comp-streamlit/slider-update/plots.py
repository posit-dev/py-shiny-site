from plotnine import aes, geom_density, geom_point, ggplot, stat_smooth, theme_light


def dist_plot(df):
    plot = (
        ggplot(df, aes(x="body_mass_g", fill="species"))
        + geom_density(alpha=0.2)
        + theme_light()
    )
    return plot


def scatter_plot(df, smoother):
    plot = (
        ggplot(
            df,
            aes(
                x="bill_length_mm",
                y="bill_depth_mm",
                color="species",
                group="species",
            ),
        )
        + geom_point()
        + theme_light()
    )

    if smoother:
        plot = plot + stat_smooth()

    return plot

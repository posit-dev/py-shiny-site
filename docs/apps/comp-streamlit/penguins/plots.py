from plotnine import aes, geom_density, geom_point, ggplot, stat_smooth, theme_light


def dist_plot(df):
    plot = (
        ggplot(df, aes(x="Body Mass (g)", fill="Species"))
        + geom_density(alpha=0.2)
        + theme_light()
    )
    return plot


def scatter_plot(df, smoother):
    plot = (
        ggplot(
            df,
            aes(
                x="Bill Length (mm)",
                y="Bill Depth (mm)",
                color="Species",
                group="Species",
            ),
        )
        + geom_point()
        + theme_light()
    )

    if smoother:
        plot = plot + stat_smooth()

    return plot

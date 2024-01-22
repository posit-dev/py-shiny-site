# ruff: noqa
## file: app.py
# Open in shinylive to see additional files

from pathlib import Path

import pandas as pd
import plotly.express as px
import shinywidgets as sw
from shiny import App, ui

appdir = Path(__file__).parent

app_ui = ui.page_fixed(
    ui.include_css(appdir / "styles.css"),
    ui.value_box(
        "Total Sales in Q2",
        "$2.45M",
        showcase=sw.output_widget("sparkline"),
        showcase_layout="bottom",
    ),
    fillable_mobile=True,
)


def server(input, output, session):
    @sw.render_widget
    def sparkline():
        economics = pd.read_csv(appdir / "economics.csv")
        fig = px.line(economics, x="date", y="psavert")
        fig.update_traces(
            line_color="#406EF1",
            line_width=1,
            fill="tozeroy",
            fillcolor="rgba(64,110,241,0.2)",
            hoverinfo="y",
        )
        fig.update_xaxes(visible=False, showgrid=False)
        fig.update_yaxes(visible=False, showgrid=False)
        fig.update_layout(
            height=100,
            hovermode="x",
            margin=dict(t=0, r=0, l=0, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        return fig


app = App(app_ui, server)


## file: economics.csv
date,pce,pop,psavert,uempmed,unemploy
2000-01-01,6535.3,280976,5.4,5.8,5708
2000-02-01,6619.7,281190,4.8,6.1,5858
2000-03-01,6685.8,281409,4.5,6,5733
2000-04-01,6671.1,281653,5,6.1,5481
2000-05-01,6707.6,281877,4.9,5.8,5758
2000-06-01,6743.9,282126,4.9,5.7,5651
2000-07-01,6764.1,282385,5.2,6,5747
2000-08-01,6799.1,282653,5.2,6.3,5853
2000-09-01,6882.9,282932,4.5,5.2,5625
2000-10-01,6888.2,283201,4.6,6.1,5534
2000-11-01,6902.4,283453,4.5,6.1,5639
2000-12-01,6945.7,283696,4.2,6,5634
2001-01-01,6977,283920,4.8,5.8,6023
2001-02-01,6995.8,284137,4.9,6.1,6089
2001-03-01,6987.9,284350,5.3,6.6,6141
2001-04-01,7001.2,284581,5,5.9,6271
2001-05-01,7047.1,284810,4.5,6.3,6226
2001-06-01,7060.7,285062,4.5,6,6484
2001-07-01,7072.2,285309,5.6,6.8,6583
2001-08-01,7108.9,285570,6.8,6.9,7042
2001-09-01,7012.8,285843,7,7.2,7142
2001-10-01,7208.4,286098,3.4,7.3,7694
2001-11-01,7167.9,286341,4.1,7.7,8003
2001-12-01,7147.7,286570,4.5,8.2,8258
2002-01-01,7174.3,286788,6.1,8.4,8182
2002-02-01,7218.3,286994,5.8,8.3,8215
2002-03-01,7237.2,287190,5.9,8.4,8304
2002-04-01,7305.4,287397,5.8,8.9,8599
2002-05-01,7282.7,287623,6.5,9.5,8399
2002-06-01,7318.2,287864,6.4,11,8393
2002-07-01,7380.4,288105,5.5,8.9,8390
2002-08-01,7401.5,288360,5.4,9,8304
2002-09-01,7391,288618,5.7,9.5,8251
2002-10-01,7430.7,288870,5.7,9.6,8307
2002-11-01,7459.7,289106,5.7,9.3,8520
2002-12-01,7512.8,289313,5.5,9.6,8640
2003-01-01,7533.1,289518,5.5,9.6,8520
2003-02-01,7535.9,289714,5.6,9.5,8618
2003-03-01,7598.4,289911,5.3,9.7,8588
2003-04-01,7621,290125,5.3,10.2,8842
2003-05-01,7628.1,290346,5.8,9.9,8957
2003-06-01,7678.6,290584,5.6,11.5,9266
2003-07-01,7738.2,290820,6.3,10.3,9011
2003-08-01,7834.5,291072,6,10.1,8896
2003-09-01,7835,291321,5.2,10.2,8921
2003-10-01,7845.7,291574,5.3,10.4,8732
2003-11-01,7899.6,291807,5.4,10.3,8576
2003-12-01,7929.2,292008,5.4,10.4,8317
2004-01-01,7987.4,292192,5,10.6,8370
2004-02-01,8019.8,292368,5,10.2,8167
2004-03-01,8076,292561,4.9,10.2,8491
2004-04-01,8088.6,292779,5.3,9.5,8170
2004-05-01,8163.2,292997,5.3,9.9,8212
2004-06-01,8147.2,293223,5.8,11,8286
2004-07-01,8218.9,293463,5.3,8.9,8136
2004-08-01,8253.1,293719,5.2,9.2,7990
2004-09-01,8321.1,293971,4.6,9.6,7927
2004-10-01,8374.6,294230,4.5,9.5,8061
2004-11-01,8420.6,294466,4.1,9.7,7932
2004-12-01,8481.5,294694,6.9,9.5,7934
2005-01-01,8470.2,294914,3.7,9.4,7784
2005-02-01,8529.2,295105,3.4,9.2,7980
2005-03-01,8569.5,295287,3.6,9.3,7737
2005-04-01,8645.6,295490,3.1,9,7672
2005-05-01,8643.9,295704,3.5,9.1,7651
2005-06-01,8724.8,295936,2.9,9,7524
2005-07-01,8829.5,296186,2.2,8.8,7406
2005-08-01,8832.4,296440,2.7,9.2,7345
2005-09-01,8885.8,296707,2.7,8.4,7553
2005-10-01,8926.6,296972,3.1,8.6,7453
2005-11-01,8938.5,297207,3.5,8.5,7566
2005-12-01,8969.6,297431,3.7,8.7,7279
2006-01-01,9059.8,297647,4.2,8.6,7064
2006-02-01,9090.1,297854,4.2,9.1,7184
2006-03-01,9122.1,298060,4.2,8.7,7072
2006-04-01,9174.8,298281,4,8.4,7120
2006-05-01,9215.1,298496,3.8,8.5,6980
2006-06-01,9240.8,298739,4,7.3,7001
2006-07-01,9322.6,298996,3.4,8,7175
2006-08-01,9321.8,299263,3.6,8.4,7091
2006-09-01,9354.7,299554,3.6,8,6847
2006-10-01,9373.2,299835,3.6,7.9,6727
2006-11-01,9380.2,300094,3.9,8.3,6872
2006-12-01,9469,300340,3.7,7.5,6762
2007-01-01,9516.3,300574,3.7,8.3,7116
2007-02-01,9546.8,300802,4.1,8.5,6927
2007-03-01,9585.1,301021,4.4,9.1,6731
2007-04-01,9615.7,301254,4.2,8.6,6850
2007-05-01,9651.3,301483,4,8.2,6766
2007-06-01,9667.3,301739,3.8,7.7,6979
2007-07-01,9709.6,302004,3.7,8.7,7149
2007-08-01,9753.9,302267,3.4,8.8,7067
2007-09-01,9797.9,302546,3.5,8.7,7170
2007-10-01,9827,302807,3.4,8.4,7237
2007-11-01,9897.8,303054,3.1,8.6,7240
2007-12-01,9908.4,303287,3.6,8.4,7645
2008-01-01,9930,303506,3.7,9,7685
2008-02-01,9913.4,303711,4.1,8.7,7497
2008-03-01,9959.4,303907,4,8.7,7822
2008-04-01,9996.8,304117,3.4,9.4,7637
2008-05-01,10053.8,304323,7.8,7.9,8395
2008-06-01,10107.9,304556,5.5,9,8575
2008-07-01,10104.7,304798,4.4,9.7,8937
2008-08-01,10094.7,305045,3.8,9.7,9438
2008-09-01,10043.5,305309,4.7,10.2,9494
2008-10-01,9960.3,305554,5.5,10.4,10074
2008-11-01,9820.8,305786,6.4,9.8,10538
2008-12-01,9730.7,306004,6.4,10.5,11286
2009-01-01,9783.8,306208,6.2,10.7,12058
2009-02-01,9766,306402,5.5,11.7,12898
2009-03-01,9718.5,306588,5.9,12.3,13426
2009-04-01,9724.8,306787,6.8,13.1,13853
2009-05-01,9748.9,306984,8.2,14.2,14499
2009-06-01,9806.9,307206,6.7,17.2,14707
2009-07-01,9841.7,307439,6,16,14601
2009-08-01,9961,307685,4.9,16.3,14814
2009-09-01,9883.4,307946,5.9,17.8,15009
2009-10-01,9931.9,308189,5.4,18.9,15352
2009-11-01,9940.5,308418,5.9,19.8,15219
2009-12-01,9998.9,308633,5.9,20.1,15098
2010-01-01,10001.8,308833,6.1,20,15046
2010-02-01,10030.6,309027,5.8,19.9,15113
2010-03-01,10089.1,309212,5.7,20.4,15202
2010-04-01,10112.9,309191.211,6.4,22.1,15325
2010-05-01,10131,309369.053,7,22.3,14849
2010-06-01,10151.4,309548.502,6.9,25.2,14474
2010-07-01,10184.7,309745.698,6.8,22.3,14512
2010-08-01,10228.2,309957.775,6.9,21,14648
2010-09-01,10249,310176.466,6.7,20.3,14579
2010-10-01,10304.7,310399.958,6.6,21.2,14516
2010-11-01,10354.7,310595.764,6.6,21,15081
2010-12-01,10392.1,310781.705,7.1,21.9,14348
2011-01-01,10435.5,310960.74,7.4,21.5,14013
2011-02-01,10470.1,311113.376,7.6,21.1,13820
2011-03-01,10550.5,311265.404,7,21.5,13737
2011-04-01,10587.6,311436.238,6.9,20.9,13957
2011-05-01,10612,311607.08,6.9,21.6,13855
2011-06-01,10636.8,311791.223,7.2,22.4,13962
2011-07-01,10677.5,311997.049,7.3,22,13763
2011-08-01,10700.6,312205.367,7.2,22.4,13818
2011-09-01,10738.1,312429.118,6.8,22,13948
2011-10-01,10753.1,312644.159,6.8,20.6,13594
2011-11-01,10759.5,312829.523,7,20.8,13302
2011-12-01,10772.2,313009.712,7.8,20.5,13093
2012-01-01,10862.1,313183.179,8,20.8,12797
2012-02-01,10953.5,313338.977,8,19.7,12813
2012-03-01,10951.8,313499.369,8.5,19.2,12713
2012-04-01,10979.7,313667.127,8.7,19.1,12646
2012-05-01,10968.6,313830.53,8.8,19.9,12660
2012-06-01,10946.3,314017.594,9.1,20.4,12692
2012-07-01,10977.2,314210.786,8.2,17.5,12656
2012-08-01,11004.1,314422.341,8,18.4,12471
2012-09-01,11061.5,314646.749,8.2,18.8,12115
2012-10-01,11099.8,314853.978,8.8,19.9,12124
2012-11-01,11136.8,315053.863,9.7,18.6,12005
2012-12-01,11140.5,315232.752,12,17.7,12298
2013-01-01,11202.8,315389.595,6.3,15.8,12471
2013-02-01,11239.6,315520.143,5.8,17.2,11950
2013-03-01,11227.1,315662.224,5.9,17.6,11689
2013-04-01,11205.4,315817.855,6.4,17.1,11760
2013-05-01,11244.6,315983.654,6.7,17.1,11654
2013-06-01,11268.8,316171.042,6.8,17,11751
2013-07-01,11296.7,316358.778,6.6,16.2,11335
2013-08-01,11329.2,316580.327,6.7,16.5,11279
2013-09-01,11366.9,316806.125,6.8,16.5,11270
2013-10-01,11419.8,317022.27,6.3,16.3,11136
2013-11-01,11487.6,317228.026,6.2,17.1,10787
2013-12-01,11517.9,317411.551,6.4,17.3,10404
2014-01-01,11512.5,317593.923,7.1,15.4,10202
2014-02-01,11566.2,317753.883,7.3,15.9,10349
2014-03-01,11643,317917.203,7.4,15.8,10380
2014-04-01,11702.6,318089.218,7.4,15.7,9702
2014-05-01,11748.4,318269.505,7.4,14.6,9859
2014-06-01,11817,318464.152,7.4,13.8,9460
2014-07-01,11860.5,318662.368,7.5,13.1,9608
2014-08-01,11944.3,318893.786,7.2,12.9,9599
2014-09-01,11957.4,319125.296,7.4,13.4,9262
2014-10-01,12023,319353.734,7.2,13.6,8990
2014-11-01,12051.4,319564.209,7.3,13,9090
2014-12-01,12062,319746.157,7.6,12.9,8717
2015-01-01,12046,319928.646,7.7,13.2,8903
2015-02-01,12082.4,320074.511,7.9,12.9,8610
2015-03-01,12158.3,320230.786,7.4,12,8504
2015-04-01,12193.8,320402.295,7.6,11.5,8526

## file: styles.css
body {
  padding-top: 1rem;
}

.bslib-value-box .plotly .modebar-container {
  display: none;
}

.shiny-ipywidget-output {
  display: flex;
  flex: 1 1 auto !important;
  width: 100%;
}

.shiny-ipywidget-output > * {
  display: flex;
  flex: 1 1 auto;
  width: 100%;
}

.shiny-ipywidget-output > * > * {
  display: flex;
  flex: 1 1 auto;
  width: 100%;
}

.shiny-ipywidget-output > * > * > * {
  display: flex;
  flex: 1 1 auto;
  width: 100%;
}



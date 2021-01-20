import udcn

rst = "dummy"
comment = "dummy"


udcn.publish_new(rst, comment, "LatestCovidData", "Alice")

LABEL_GIVEN_BY_ALICE = "LatestCovidData"
data_source = udcn.get_label_content(LABEL_GIVEN_BY_ALICE)
udcn.publish_new(rst, val_comment, "CovidPrediction",
                 "Betty", [LABEL_GIVEN_BY_ALICE, ])

LABEL_FROM_BETTY = "CovidPrediction"
total_val = udcn.get_label_content(LABEL_FROM_BETTY)
pre1 = udcn.File("predict_1.png")
udcn.publish_new(pre1, "Predict image for week one",
                 "CovidPredictionPic", "Charlie",
                 [LABEL_FROM_BETTY, ])
udcn.publish_new(least_list,
                 "Ten states with the fewest COVID cases",
                 "TenStatesWithFewestCovid",
                 "Charlie", [LABEL_FROM_BETTY, ])

udcn.publish_update(rst, comment, "LatestCovidData", "Alice")

PREV_LABEL = "CovidPrediction"
LABEL_GIVEN_BY_ALICE = "LatestCovidData"
data_source = udcn.get_label_content(LABEL_GIVEN_BY_ALICE)
udcn.publish_update(rst, val_comment, PREV_LABEL,
                    "Betty", [LABEL_GIVEN_BY_ALICE, ])

LABEL_FROM_BETTY = "CovidPrediction"
PREV_PIC = "CovidPredictionPic"
PREV_VID = "TenStatesWithFewestCovid"
total_val = udcn.get_label_content(LABEL_FROM_BETTY)
udcn.publish_update(pre1, "Second week prediction image",
                    PREV_PIC, "Charlie", [LABEL_FROM_BETTY,])
udcn.publish_update(least_list, "Ten states with the \
                    fewest COVID cases", PREV_VID,
                    "Charlie", [LABEL_FROM_BETTY, ])

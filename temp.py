def predict_with_regression_model(data_source):
    pass

"""Code from the second researcher"""
import kgpl
temp_var = kgpl.load_var("http://kgplServerOne/var/0")
data_source = kgpl.load_val(temp_var.val_id).val
rst = predict_with_regression_model(data_source) # rst is a dict containing the result of prediction.

val_comment = "Prediction for COVID-19 cumulative positive cases for all states in the US for" + date_to_predict # date_to_predict is a string variable containing the date for prediction.
var_comment = "Prediction for COVID-19 cumulative positive cases for all states in the US in the next day. Data source from http://kgplServerOne/var/0."
myval = kgpl.value(rst, val_comment) # Create a KGPLValue.
kgpl.variable(myval.vid, var_comment) # Create a KGPLVariable.

import knps

def person4():
    idSharedbyPerson3 = knps.server_url + "/var/2"
    idSharedbyPerson2 = knps.server_url + "/var/1"
    idSharedbyPerson1 = knps.server_url + "/var/0"
    # the actual number of positive cases of each state
    updated_dict_val = knps.load_var(idSharedbyPerson1).getConcreteVal()
    updated_dict = updated_dict_val.getConcreteVal()
    # 10 states that actually have the least positive cases
    L = [(k, v) for (k, v) in updated_dict.items()]
    L.sort(key=lambda x: x[1])
    actual_least_list = []
    for i in range(1, 11):
        actual_least_list.append(L[i][0])
    # the number of positive cases of each state predicted yesterday
    predicted_dict_var = knps.load_var(idSharedbyPerson2)
    l = knps.get_history(predicted_dict_var)
    assert(len(l)>=2)
    yesterday_predicted_dict = knps.load_val(l[1]).getConcreteVal()
    # the least 10 states predicted by yesterday
    predicted_least_list_var = knps.load_var(idSharedbyPerson3)
    ll = knps.get_history(predicted_least_list_var)
    assert(len(ll)>=2)
    predicted_least_list = knps.load_val(ll[1]).getConcreteVal()
    # print the deviation of prediction from reality
    dict_of_deviation = {}
    for state, inform in updated_dict.items():
        assert(state in yesterday_predicted_dict)
        dict_of_deviation[state] = inform[0][1] - yesterday_predicted_dict[state]
    print("The prediction deviation of each state:\n")
    print(dict_of_deviation)
    print("The 10 states that actually have the least positive cases:\n")
    print(actual_least_list)
    print("The 10 states that were expected to have the least positive cases:\n")
    print(predicted_least_list)
    print("The difference:\n")
    print(set(actual_least_list)-set(predicted_least_list))
person4()

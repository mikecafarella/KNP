function handleInput() {
    var user_code = document.getElementById("user_code").value;
    if(!user_code.includes("(") || user_code.endsWith("(") || user_code.endsWith(".") || user_code.endsWith("|") || user_code.endsWith(")")){
        return;
    }
    var KG_params = user_code.substring(user_code.indexOf("(") + 1).split("|");
    var last_param = KG_params[KG_params.length - 1].split(".");
    var search_string = last_param[last_param.length - 1];
    if(last_param.length > 1){
        var type = "property";
    }
    else{
        var type = "item";
    }
    // console.log(KG_params);
    // console.log(type);
    // return;

    $("#entity_list")
      .empty()
    
    $.ajax({
        url: "https://www.wikidata.org/w/api.php",
        type: "GET",
        dataType: "jsonp",
        data: {
            'action': 'wbsearchentities',
            'format': 'json',
            'language': 'en',
            'search': search_string,
            'limit': 10,
            'type': type
        },
        success: function(response) {
            var search_results = response['search'];
            var entities = search_results.map(function(search_rst) {
                var option = document.createElement('option');
                option.value = search_rst['id'];
                option.text = search_rst['id'] + "(" + search_rst['label'] + ")" + ": " + search_rst['description'];
                option.onclick = function () {
                    document.getElementById("user_code").value = user_code.replace(search_string, option.value)
                    $("#entity_list")
                      .empty();
                };
                return option;
              });
            $("#entity_list")
            .empty()
            .append(entities);
        }
      });
}


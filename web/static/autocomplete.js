String.prototype.replaceAt = function(index, replacement) {
    return this.substr(0, index) + replacement+ this.substr(index + replacement.length);
}


function handleInput(e) {
    var user_code = document.getElementById("user_code").value;
    
    var cursor_pos = e.target.selectionStart;
    var char_before_cursor = user_code.charAt(cursor_pos - 1);
    // console.log(char_before_cursor);
    if(!user_code.includes("(") || char_before_cursor === ")" || char_before_cursor === "." || char_before_cursor === "|" || char_before_cursor === "(" || cursor_pos <= user_code.indexOf("(")){
        $("#entity_list")
          .empty()
        return;
    }
    // console.log("here");
    var replaced_user_code = user_code.replace(/[^a-zA-Z0-9 ]/g, "|");
    // console.log(replaced_user_code);
    var search_string_start = replaced_user_code.lastIndexOf("|", cursor_pos - 1) + 1;
    var search_string_end = replaced_user_code.indexOf("|", cursor_pos);
    if(search_string_end === -1){
        search_string_end = replaced_user_code.length;
    }
    var search_string = replaced_user_code.substring(search_string_start, search_string_end);
    // console.log(search_string);

    if(user_code.charAt(search_string_start - 1) === "."){
        var type = "property";
    }
    else{
        var type = "item";
    }

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
                    document.getElementById("user_code").value = user_code.substring(0, search_string_start) + search_rst['id'] + ":" + search_rst['label'] + user_code.substring(search_string_end);
                    // document.getElementById("IDs").value += seperator + search_rst['id']; 
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
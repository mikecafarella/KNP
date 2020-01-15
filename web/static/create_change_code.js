
function code_submit(){
    var editor = ace.edit("editor");
    var code = editor.getValue();
    var name = document.getElementById("name").innerHTML;
    var type = document.getElementById("type").value;
    // console.log(type);
    $.ajax({
        url: "",
        type: "POST",
        data: {
            'name': name,
            'code': code,
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


function create_code(){
    var editor = ace.edit("editor");
    var code = editor.getValue();
    var name = document.getElementById("name").value;
    var type = document.getElementById("type").value;
    $.ajax({
        url: "/create",
        type: "POST",
        data: {
            'name': name,
            'code': code,
            'type': type
        },
        success: function(response) {
            alert("success!")
        }
      });
}
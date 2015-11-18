$("#uid").attr("value",-1); 

function fresh_id(sig) {

    $.post(get_fresh_id_url,{ 'uid' : $("#uid").val() , 'sig' : sig},function (dd) {
            
            if(dd['uid'] == -1) {
                $("#qinfo").text("No results in this stream"); 
                d3.select("#choices").selectAll("div .val_choice").remove()  
                console.log("NO RESULTS!");
                return;
            }

            var name = dd['name'];
            var info = dd['info'];
            var possibles = dd['possibles'];

            d3.select("#qinfo").attr('font', '32').attr('font', 'bold').text("Name: "+name+"     Organization: "+info);
      
            d3.select("#choices").selectAll("div").remove();

            var li = d3.select("#choices").selectAll("div .val_choice").data(possibles);
            li.enter().append("div");
            li.exit().remove();

            li.selectAll("div").remove();

            li.attr("class","row");

            var img_row = li.append("div").attr("class","col-md-5 col-md-offset-3 media");

            img = img_row.append('div').attr('class', 'media-left');

            img.append('a').attr('href', '#');
            img.append("img").attr("class", "media-object img-rounded").attr("src",function(d) {
                    return d[3];
              }).attr("width", "110px").attr("alt","Media Object");         
            
            var info = img_row.append("div").attr("class", "media-body");

            var name_title = info.append("h4");

            name_title.text(function(d) {
                    return d[1];});
            name_title.append("small").text(function(d) {
                    return "  \t@" + d[0]+"   ";});

            var tinfo = info.append('table');
            var tr = tinfo.append("tr").attr("class", "head");
            tr.append("td").text("Followers");
            tr.append("td").text("Following");
            tr.append("td").text("Tweets");
            tr.append("td").text("Connected");
            
            tr = tinfo.append("tr").attr("class", "second");
            tr.append("td").text(function(d) {return d[4]});
            tr.append("td").text(function(d) {return d[5]});
            tr.append("td").text(function(d) {return d[6]});   
            tr.append("td").text(function(d) {return d[8]});

            info.append("div").style("overflow-y","auto").style("text-align","left").text(function(d) {
                    var desc = d[2] + "\n";  
                    if(d[7].length > 0)
                        desc += d[7] + ". ";
                    return desc;
                });

            info.append('hr');

            li.append("div").attr("class","col-md-2 check").append("input").attr("type","checkbox").attr("align", "center").attr("id",function(d,i) {
                    return "validate-" + i;
                }).style("width","30px");

            $("#uid").attr("value",dd['uid']);       
        });
}

function submit_validation(sig) {

    var li = d3.select("#choices").selectAll("div .check");

    var ret = [];

    var msg = "eval";
    if (sig == 0) msg = "eval_unsure";

    li.each(function (d,i) {
            if($("#validate-" + i).is(':checked')) {
                var tw_id = d[0];
                ret.push(tw_id);
            }
        });

    $.post( submit_url, { 'uid' : $("#uid").val() , 'msg': msg, 'valid_handles[]' : ret },function(data){
        fresh_id(0);
    });
}

fresh_id(0);
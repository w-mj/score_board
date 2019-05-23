let ws = new WebSocket('ws://127.0.0.1:8001');
ws.onmessage = function(msg) {
    msg = msg.data;
    // console.log(msg);
    msg = JSON.parse(msg);
    if (msg['act'] !== 'score')
        return null;
    update_table(msg['score'])
};


$(document).ready(()=>{
    // setInterval(update, 1000);
    update();
});

function send_change(group, item, act) {
    console.log(group + ' ' + item + ' ' + act);
    $.ajax({
        url: 'http://127.0.0.1:8000',
        method: 'POST',
        data: JSON.stringify({act: 'score', score: [group, item, act]}),
        contentType: 'text/plain',
        success: (d)=> {
            console.log(d)
        }
    })
}

function send_out(group, out) {
    console.log(group + ' ' + out);
    $.ajax({
        url: 'http://127.0.0.1:8000',
        method: 'POST',
        data: JSON.stringify({act: 'out', out: [group, out]}),
        contentType: 'text/plain',
        success: (d)=> {
            console.log(d)
        }
    })
}

function set_sort(s) {
    console.log('sort ' + s);
    $.ajax({
        url: 'http://127.0.0.1:8000',
        method: 'POST',
        data: JSON.stringify({act: 'sort', sort: s}),
        contentType: 'text/plain',
        success: (d)=> {
            console.log(d)
        }
    })
}

function update_table(data) {
    // console.log(data);
    let table = $("#score-table").html(' ');
    let table_header_str = "<tr><th>组名</th>";
    for (let i in data[0]) {
        table_header_str += "<th>" + data[0][i] + "</th>";
    }
    table_header_str += "<th>操作</th></tr>";
    table.append("<thead>" + table_header_str + "</thead>");
    table.append("<tbody>");
    for (let i in data[1]) {
        let row = data[1][i];
        let table_item_str = "<tr>";
        table_item_str += "<td>" + row['name'] + "</td>";
        // console.log(row);
        for (let s in row['scores']) {
            table_item_str += "<td>";
            table_item_str += '<div class="btn-group btn-group-sm" role="group">' +
                '<button type="button" class="btn btn-success" onclick="send_change(\''+row['name']+'\','+s+',1)">+</button>' +
                '<button type="button" class="btn btn-primary">' + row['scores'][s] +'</button>' +
                '<button type="button" class="btn btn-danger" onclick="send_change(\''+row['name']+'\','+s+',-1)">-</button>' +
                '</div></td>';
        }
        if (row['out'])
            table_item_str += '<td><button class="btn btn-sm btn-primary" onclick="send_out(\''+row['name'] +'\', false)">恢复</button></td>';
        else
            table_item_str += '<td><button class="btn btn-sm btn-danger" onclick="send_out(\''+row['name'] +'\', true)">淘汰</button></td>';

        table_item_str += "</tr>";
        table.append(table_item_str);
    }
    table.append("</tbody>");
}

function update() {
    $.ajax({
        url: 'http://127.0.0.1:8000',
        method: 'GET',
        dataType: 'json',
        success: update_table
    });
}

function responder_reset() {
    ws.send('{"act": "reset"}');
}

function responder_start() {
    ws.send('{"act": "start"}');
}
let url = window.location.origin;
let ws_url = "ws:" + url.split(':')[1] + ":8001";

let ws = new WebSocket(ws_url);
ws.onmessage = function(msg) {
    msg = msg.data;
    // console.log(msg);
    msg = JSON.parse(msg);
    if (msg['act'] === 'score') {
        update_table(msg['score']);
    } else if (msg['act'] === 'responder_state') {
        let state = '';
        switch(msg['state'][0]) {
            case 0:
                state='已抢答';
                break;
            case 1:
                state='正在抢答';
                break;
            case 2:
                state='抢答未开始';
                break;
            default:
                state='??' + msg['state'][0];
                break;
        }
        $("#responder-state").html(state);
        $("#responder-cnt").html(msg['state'][1]);
    }
};


$(document).ready(()=>{
    // setInterval(update, 1000);
    update();

    setInterval(()=>{
        ws.send('{"act": "responder_state"}')
    }, 1500);
});

function send_change(group, item, act) {
    console.log(group + ' ' + item + ' ' + act);
    $.ajax({
        url: url,
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
        url: url,
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
        url: url,
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
        url: url,
        method: 'GET',
        dataType: 'json',
        success: update_table
    });
}

function responder_reset() {
    ws.send('{"act": "reset"}');
    ws.send('{"act": "responder_state"}');
}

function responder_start() {
    ws.send('{"act": "start"}');
    ws.send('{"act": "responder_state"}');
}
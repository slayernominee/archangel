function sendNotification(type, title, text='', duration=0) {
    id = Math.random();
    info = `<div class="Message" id="` + String(id) + `">
    <div class="Message-icon">
    <i class="fa fa-bell-o"></i>
    </div>
    <div class="Message-body" id="` + String(id) + `-body">
    <p>` + String(title) + `</p>
    <p class="u-italic">` + String(text) + `</p>
    </div>
    <button class="Message-close js-messageClose" onclick="document.getElementById('` + String(id) + `').style.display = 'none';"><i class="fa fa-times"></i></button>
    </div>`
    warning = `<div class="Message Message--orange" id="` + String(id) + `">
    <div class="Message-icon">
    <i class="fa fa-exclamation"></i>
    </div>
    <div class="Message-body" id="` + String(id) + `-body">
    <p>` + String(title) + `</p>
    <p class="u-italic">` + String(text) + `</p>
    </div>
    <button class="Message-close js-messageClose" onclick="document.getElementById('` + String(id) + `').style.display = 'none';"><i class="fa fa-times"></i></button>
    </div>`
    success = `<div class="Message Message--green" id="` + String(id) + `">
    <div class="Message-icon">
    <i class="fa fa-check"></i>
    </div>
    <div class="Message-body" id="` + String(id) + `-body">
    <p>` + String(title) + `</p>
    <p class="u-italic">` + String(text) + `</p>
    </div>
    <button class="Message-close js-messageClose" onclick="document.getElementById('` + String(id) + `').style.display = 'none';"><i class="fa fa-times"></i></button>
    </div>`
    error = `
    <div class="Message Message--red" id="` + String(id) + `">
    <div class="Message-icon">
    <i class="fa fa-times"></i>
    </div>
    <div class="Message-body" id="` + String(id) + `-body">
    <p>` + String(title) + `</p>
    <p class="u-italic">` + String(text) + `</p>
    </div>
    <button class="Message-close js-messageClose" onclick="document.getElementById('` + String(id) + `').style.display = 'none';"><i class="fa fa-times"></i></button>
    </div>`
    
    if (type == 'info') {
        messages.innerHTML += info;
    } else if (type == 'warning') {
        messages.innerHTML += warning;
    } else if (type == 'success') {
        messages.innerHTML += success;
    } else if (type == 'error') {
        messages.innerHTML += error;
    }
    deleteMessageAfter(id, duration);
    /* 
    Add A Button to an Notification
    <button class="Message-button" id="js-helpMe">Yikes, help me please!</button>
    */
    return String(id);
}
function deleteMessageAfter(id, duration) {
    if (duration != 0) {
        setTimeout(function () {
            document.getElementById(String(id)).remove();
        }, duration);
    }
}

function checkNotifications() {
    $.ajax({
        type: "POST",
        url: "/get/notifications",
        data: {
        },
        success: function(data) {
            var notifications = data['notifications'];
            for (noti in notifications) {
                id = sendNotification(notifications[noti]['type'], notifications[noti]['title'], notifications[noti]['text'], notifications[noti]['duration']);
                for (i in notifications[noti]['buttons']) {
                    var button = notifications[noti]['buttons'][i];
                    bodyArea = document.getElementById(id + '-body');
                    bodyArea.innerHTML += `<button class="Message-button" onclick="` + button['onclick'] + `">` + button['text'] + `</button>`;
                }
            }
        }
    });
}
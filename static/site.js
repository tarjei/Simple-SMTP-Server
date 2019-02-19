var refreshRate = 5;
var messageCache = {};
var refreshInbox = function() {
  setTimeout(function() {
    $.get("/api/has_new", function(data) {
      if (data == "true") window.location = window.location;
      else refreshInbox();
    });
  }, refreshRate * 1000);
};

var showMessage = function(id) {
  if (!messageCache["" + id]) return;

  msgBox = $(".msgBox");
  msgRow = $(".msgRow[msgId=" + id + "]");

  if (msgRow.hasClass("msgOpen")) {
    msgRow.removeClass("msgOpen");
    msgBox.hide();
    return;
  } else {
    $(".msgRow").removeClass("msgOpen");
    msgRow.addClass("msgOpen");
  }

  msgRow.addClass("msgRead");
  msgBox.show();

  msgRow.after(msgBox);

  message = messageCache["" + id];
  console.log(message);
  msgBox.html("<pre>" + message.data + "</pre>");
};

$(document).ready(function() {
  $(".msgRow")
    .css("cursor", "hand")
    .click(function() {
      id = $(this).attr("msgId");
      console.log(id);
      if (id == "") return;
      if (!messageCache["" + id]) {
        $.get("/api/read/" + id, function(msg) {
          if (msg == false || msg == "false") return;

          if (typeof msg == "string") msg = JSON.parse(msg);

          messageCache["" + id] = msg;
          showMessage(id);
        });
      } else showMessage(id);
    });

  $(".msgBox").hide();

  $(".timeField").each(function(e) {
    var val = $(this).text();
    var d = new Date(0);
    d.setUTCSeconds(parseInt(val));
    $(this).html(d.toDateString());
  });
});

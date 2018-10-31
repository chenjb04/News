function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();
        var params = {
            "old_password": $("input[name='old_password']").val(),
            "new_password": $("input[name='new_password']").val(),
            "repeat_new_password": $("input[name='repeat_new_password']").val(),
        };
        // 修改密码
        $.ajax({
            url: "/user/pass_info",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // 修改成功
                    alert("修改成功");
                    window.location.reload()
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
});

class User
    template : window.Handlebars.compile($.trim($("#message-template").html()))
    constructor : (@user_nick) ->
        console.log "Initialized"


    init : () ->
        console.log "Initialized"
        do @loadTimeline

    loadTimeline: () ->
        $.getJSON("/ajax/user/#{@user_nick}/timeline",
            {_: new Date().getTime(), after_id: @lastMessage or -1},
            (data) =>
                console.log(data)
                $("#timeline").append(@template(
                    message: data.timeline
                ))
        )



$ ->
    user_nick = $("#user_nick").val()
    user = new User(user_nick)
    user.init()




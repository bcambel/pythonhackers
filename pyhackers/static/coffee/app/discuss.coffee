
class @Discuss

    constructor: (@discussion_id) ->
        @lastMessage = null
        @template = window.Handlebars.compile($.trim($("#message-template").html()))
        console.log "Discussion started #{@discussion_id}"

    init: () =>
        window.setInterval(@reload, 10000)
        do @reload

    reload: () =>
        @discussion_id
        $.getJSON('/ajax/discuss/'+@discussion_id+'/messages',
            {_: new Date().getTime(), after_id: @lastMessage or -1},
            (data) =>
                console.log(data)
                @lastMessage = data.discussion.last_message

                $(".posts").append(@template(
                    message: data.posts
                ))
        )


$ ->
    discuss = new Discuss($("#discussion_id").val())
    discuss.init()
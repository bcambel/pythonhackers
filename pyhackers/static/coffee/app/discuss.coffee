
class @Discuss

    constructor: (@discussion_id) ->
        @lastMessage = null
        @template = window.Handlebars.compile($.trim($("#message-template").html()))
        console.log "Discussion started #{@discussion_id}"

    init: () =>
        if !@discussion_id?
            return
        window.setInterval(@reload, 10000)
        do @reload

    reload: () =>

        $.getJSON("/ajax/discuss/#{@discussion_id}/messages",
            {_: new Date().getTime(), after_id: @lastMessage or -1},
            (data) =>
                console.log(data)
                @lastMessage = data.discussion.last_message

                $(".posts").append(@template(
                    message: data.posts
                ))
        )

    discussDialog: () =>
        $template = $($("#discuss-template").html())

        $(body).append($template)
        $template.modal()


$ ->
    discus_id = $("#discussion_id").val()

    discuss = new Discuss(discus_id)
    discuss.init()
    $(document).on 'click', '[href="#discuss-dialog"]', discuss.discussDialog
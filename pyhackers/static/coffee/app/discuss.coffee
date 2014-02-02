
class @Discuss

    constructor: (@discussion_id) ->
        @lastMessage = null
        @template = window.Handlebars.compile($.trim($("#message-template").html()))
        console.log "Discussion started #{@discussion_id}"

    init: () =>
        if !@discussion_id?
            return

        $(document).on("ajax:success","#discussion-message", @onDiscussionMessage)
        $(document).on("ajax:error","#discussion-message", @onDiscussionMessageError)
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

    onDiscussionMessageError: (event) ->
        Messenger().post
            message:"Something went wrong! Try again"
            type:"error"

    onDiscussionMessage : (event, data) ->
        unless data.id
            Messenger().post
                message:"Something went wrong! Try again"
                type:"error"
            return

        $form = $(event.currentTarget)
        $form.find("textarea").val("")
        Messenger().post
            message:"Message has been sent!"
            type:"success"


    discussDialog: () =>
        $template = $($("#discuss-template").html())

        $(body).append($template)
        $template.modal()

    discussionFollowAction: () ->
        return
        # Take care of the Discussion Follow/UnFollow events

        # turn the buttons follow/unfollow
        # input[type='hidden'] fix
        # Change the button appearance


$ ->
    discus_id = $("#discussion_id").val()

    discuss = new Discuss(discus_id)
    discuss.init()
    $(document).on 'click', '[href="#discuss-dialog"]', discuss.discussDialog
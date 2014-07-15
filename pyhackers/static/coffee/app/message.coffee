
# Our Message interface to internet


class @Message
    constructor: ()->
        @editTemplate = window.Handlebars.compile($.trim($("#edit-message-template").html()))
        do @listen

    listen : () ->
        $(document).on 'click', '[data-trigger="message"]', (evt) =>
            @showMessage(evt)
        $(document).on 'click', '[data-trigger="upvote"]', (evt) =>
            @upvote(evt)
        $(document).on 'click', '[data-action="edit-message"]', (evt) =>
            @editMessage(evt)

        $(document).on 'click', '[data-action="delete-message"]', (evt) =>
            @deleteMessage(evt)

    upvote: (evt) ->
        $(evt.target).css({color:'orange'})
        messageId = $(evt.currentTarget).parents('[data-message-id]').attr("data-message-id")
        evt.stopPropagation()
        evt.preventDefault()
        $.post("/ajax/message/#{messageId}/upvote", {message:messageId}, (data) ->
            console.log data
        )


    showMessage : (evt) =>
        vex.dialog.open
            message: "Whats up"
            input: """
<textarea rows="3" name="message" required ></textarea>
"""
            buttons: [
                $.extend({}, vex.dialog.buttons.YES, text: 'Post')
                $.extend({}, vex.dialog.buttons.NO, text: 'Back' , class: 'pull-left')
            ]
            callback: (data) ->
                return console.log('Cancelled') if data is false

                console.log 'Username', data.message

                $.post('/ajax/message/new', {message:data.message}, () ->
                    console.log "Ok"
                    Messenger().post
                        message:"Message has been sent"
                        type:"success"
                )

    deleteMessage: (evt) =>
        $target = $(evt.target)
        href = $target.attr("href")

        $.post href, {} , (response) ->
            if response.ok
                $target.parents("[data-message-id]").remove()

        evt.stopPropagation()
        evt.preventDefault()

    editMessage: (evt) =>

        $messagePanel = $(evt.target).parents('[data-message-id]')
        messageId = $messagePanel.attr('data-message-id')

        $messageContainer = $messagePanel.find(".panel-body .message")

        $messageContainer.html(@editTemplate({id: messageId}))

        $.getJSON "/ajax/post/#{messageId}", (response) =>
            $messageContainer.find("textarea").val(response.data.text).autosize()

        $messageContainer.find("form").on "ajax:success", (evt, response) =>
            if response.ok
                $messageContainer.html(response.data.html)
            else
                alert("Failed to update.")

        evt.stopPropagation()
        evt.preventDefault()


jQuery ->
    msg = new Message()

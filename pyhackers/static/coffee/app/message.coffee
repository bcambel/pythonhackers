
# Our Message interface to internet


class @Message
    constructor: ()->
        do @listen

    listen : () ->
        $(document).on 'click', '[data-trigger="message"]', (evt) =>
            @showMessage(evt)
        $(document).on 'click', '[data-trigger="upvote"]', (evt) =>
            @upvote(evt)

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

jQuery ->
    msg = new Message()

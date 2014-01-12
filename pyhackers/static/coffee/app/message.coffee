
# Our Message interface to internet


class @Message
    constructor: ()->
        do @listen

    listen : () ->
        $(document).on 'click', '[data-trigger="message"]', (evt) =>
            @showMessage(evt)


    showMessage : (evt) =>
        console.log("ok")


jQuery ->
    msg = new Message()
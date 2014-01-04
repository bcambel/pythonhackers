
Application = {
    begin : () ->
        do @formSubmitter
        @

    formSubmitter : () ->

        $('form[data-remote]').submit (evt) ->
            evt.preventDefault()
            evt.stopPropagation()

            unless window.session.hasOwnProperty("id")
                document.location = '/authenticate'
                return

            $this = $(this)
            action = $this.attr("action")
            postData = $this.serializeArray()
            $.post(action, postData)


        $('[data-toggle="tooltip"]').tooltip()
}


do Application.begin

Application = {
    begin : () ->
        do @formSubmitter
        @

    formSubmitter : () ->
        $('form[data-remote]').submit (evt) ->
            $this = $(this)
            action = $this.attr("action")
            postData = $this.serializeArray()
            $.post(action, postData)
            evt.preventDefault()
            evt.stopPropagation()
}


do Application.begin
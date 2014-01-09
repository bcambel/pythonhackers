
Application = {

    begin : () ->
        $(@load)

    load: () =>
        do Application.formSubmitter
        $("#mc_embed_signup").on("show.bs.modal", ->
            mixpanel.track("signup-popup")
        )

        mixpanel.track_links(".navbar a", "navlink", (el) ->
            href = $(el).attr("href")
            if href == "#mc_embed_signup"
                return false

                path: href.replace("#","")
                referrer: document.referrer
        )
        _.defer( -> mixpanel.track("visit", { path: document.location.pathname }))

    captureSubmit : ($el) ->
        action = $el.attr("action")
        if !!action?
            action = action.replace("/ajax/","")

        id = $('[name="id"]',$el).val()
        slug = $('[name="slug"]',$el).val()
        mixpanel.track action,
            referrer: document.referrer
            id: id
            slug: slug


    formSubmitter : () ->

        $('form[data-remote]').submit (evt) ->
            evt.preventDefault()
            evt.stopPropagation()
            Application.captureSubmit($(evt.currentTarget))

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

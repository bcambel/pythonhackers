
img_quicky = (path,ref,cp) ->
    ts = (new Date()).getTime()
    i=document.createElement("img")
    i.setAttribute('src', "http://pythonhackers.com/gitbeacon?_=#{ts}&r=#{ref}&p=#{path}&cp=#{cp}")
    i.setAttribute('alt', 'a')
    i.setAttribute('height', '1px')
    i.setAttribute('width', '1px')
    document.body.appendChild(i)


Application = {

    begin : () ->
        $(@load)

    mixevents: () ->
        unless !!window.mixpanel?
            return

        $("#mc_embed_signup").on("show.bs.modal", ->
            mixpanel.track("signup-popup")
        )
        $(document).on('click','.navbar a', (evt) ->
            href = $(evt.currentTarget).attr('href')
            img_quicky(encodeURIComponent(href), encodeURIComponent(document.referrer), encodeURIComponent(document.location.pathname))
            evt.stopPropagation()
            evt.preventDefault()

            window.setTimeout( =>
                document.location = href
            , 300)
        )
        _.defer( -> mixpanel.track("visit", { path: document.location.pathname }))


    load: () =>
        do Application.formSubmitter
        do Application.mixevents

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
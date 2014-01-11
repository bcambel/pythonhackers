
img_quicky = (path,ref,cp, htag) ->
    ts = (new Date()).getTime()
    url = "http://pythonhackers.com/gitbeacon?_=#{ts}&r=#{ref}&p=#{path}&cp=#{cp}"

    i=document.createElement("img")
    i.setAttribute('src', url )
    i.setAttribute('alt', 'a')
    i.setAttribute('height', '1px')
    i.setAttribute('width', '1px')
    document.body.appendChild(i)


Application = {

    begin : () ->
        $(@load)

    mixevents: () ->

        $("#mc_embed_signup").on("show.bs.modal", ->
            mixpanel.track("signup-popup")
        )

        $(document).on('click','a', (evt) ->
            href = $(evt.currentTarget).attr('href')

            hashtag = href[0] == "#"

#            debugger

            img_quicky(encodeURIComponent(href), encodeURIComponent(document.referrer), encodeURIComponent(document.location.pathname),hashtag)

            if hashtag
                return

            evt.stopPropagation()
            evt.preventDefault()

            window.setTimeout( =>
                document.location = href
            , 300)
        )

#        _.defer( -> mixpanel.track("visit", { path: document.location.pathname }))


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
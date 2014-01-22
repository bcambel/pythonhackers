
class @Beacon
    constructor: () ->
        @url = "http://pythonhackers.com/gitbeacon?"

    view: () =>
        p =
            t: "v"

        @notify(@getQs(p))

    notify: (params) =>
        reqUrl = @url + params
        if PythonHackers.opts.prod == 0
            @addImage(reqUrl)
        else
            $.get(reqUrl)

    getQs: (dict) ->
        params = []

        _.extend dict,
            env: PythonHackers.opts.prod
            start: PythonHackers.opts.startTime
            ts: do @_ts
            r: document.referrer
            cp: document.location.href
            ua: navigator.userAgent
            scr: screen.width+'x'+screen.height

        for key of dict
            val = encodeURIComponent(dict[key])
            params.push("#{key}=#{val}")

        params.join('&')

    _ts : () ->
        (new Date()).getTime()

    addImage: (src) ->
        i=document.createElement("img")
        i.setAttribute('src', src )
        i.setAttribute('alt', 'a')
        i.setAttribute('height', '1px')
        i.setAttribute('width', '1px')
        document.body.appendChild(i)

    click: (path, htag) ->
        qs = @getQs
            t: "c"
            p: path

        url = @url + qs

        if htag or PythonHackers.opts.prod == 0
            @notify(qs)
            return

        @addImage(url)

Application = {

    begin : () ->
        @dog = new Beacon()

        $(@load)

    mixevents: () ->

#        $("#mc_embed_signup").on("show.bs.modal", =>
#            @dog.click("#signup","#mc_embed_signup")
##            mixpanel.track("signup-popup")
#        )

#        $(document).on('click','a', (evt) =>
#            href = $(evt.currentTarget).attr('href')
#
#            hashtag = href[0] == "#"
#
#            @dog.click(href, hashtag)
#
#            if hashtag
#                return
#
#            evt.stopPropagation()
#            evt.preventDefault()
#
#            window.setTimeout( =>
#                document.location = href
#            , 200)
#        )


        _.defer( =>  do @dog.view )
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
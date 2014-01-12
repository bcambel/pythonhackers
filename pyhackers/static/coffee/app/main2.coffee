
img_quicky = (path) ->
    oImg=document.createElement("img")
    oImg.setAttribute('src', 'http://pythonhackers.com/gitbeacon?_=1&#{path}')
    oImg.setAttribute('alt', 'na')
    oImg.setAttribute('height', '1px')
    oImg.setAttribute('width', '1px')
    document.body.appendChild(oImg)

class @Watchdog
    constructor = (mx) ->
        @mx = mx

    track : (event, options={}) =>
        console.log( "Tracking #{event} with #{options}")
        @forward('track', event, options)

    track_links : (selector, event, options={}) =>
        console.log( "Tracking Links #{selector} #{event} #{options}")
        @forward('track_links', selector, event, options)

    track_click_quick: () =>
        img_quicky("test=test")

    forward: (method) ->
        args = []
        first = true
        for el in arguments
            unless first
                args.push(el)
            if first
                first = false

        try
            a = args.shift()
            b = args.shift()
            if args.length >= 1
                c = args.shift()
            debugger
            if args.length is 2
                window.mixpanel[method](a,b)
            else
                window.mixpanel[method](a,b,c)
        catch e
            console.log(e)

class Application

    constructor: () ->
        # hello
        this

    begin : () ->
        $(@load)

    activityTrack: () =>

        $("#mc_embed_signup").on("show.bs.modal", =>
            @dog.track("signup-popup")
        )
        $(document).on("click", ".navbar a" , (evt) =>
            href = $(evt.currentTarget).attr("href")
            if href == "#mc_embed_signup"
                return false

            @dog.track("navlink",
                path: href.replace("#","")
                referrer: document.referrer
            )

            evt.stopPropagation()
            evt.preventDefault()

            window.setTimeout( =>
                document.location = href
            , 500)

            return false

        )

        _.defer( => @dog.track("visit", { path: document.location.pathname }))


    load: () =>
        @dog = window.mixpanel #or new Watchdog()
        do @formSubmitter
        do @activityTrack
#        window.setTimeout(=>
#        ,500)

    captureSubmit : ($el) ->

        action = $el.attr("action")
        if !!action?
            action = action.replace("/ajax/","")

        id = $('[name="id"]',$el).val()
        slug = $('[name="slug"]',$el).val()

        @dog.track action,
            referrer: document.referrer
            id: id
            slug: slug


    formSubmitter : () ->

        $('form[data-remote]').submit (evt) =>
            evt.preventDefault()
            evt.stopPropagation()
            @captureSubmit($(evt.currentTarget))

            unless window.session.hasOwnProperty("id")
                document.location = '/authenticate'
                return

            $this = $(this)
            action = $this.attr("action")
            postData = $this.serializeArray()
            $.post(action, postData)


        $('[data-toggle="tooltip"]').tooltip()



window.PythonHackers = new Application()
do PythonHackers.begin

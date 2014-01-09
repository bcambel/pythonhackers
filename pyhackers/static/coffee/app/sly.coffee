#global Sly
jQuery ($) ->

    $items = $("#frame")
    template = Handlebars.compile($('#project-template').html())
    start = 0
    newItems = (response) ->
        start += 50
        renderItems(response)

    renderItems = (response) ->
        $items.append(template({projects:response.data, start:start}))

    next = () ->
        $.getJSON("/fancy.json?start=#{start}", newItems)

    $(document).on("click", "#next", (evt) ->
        next()
        evt.stopPropagation()
        evt.preventDefault()
    )

    next()
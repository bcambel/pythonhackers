
class @Discuss

    constructor: (@discussion_id) ->
        console.log "Discussion started #{@discussion_id}"

    init: () =>
        window.setInterval(@reload, 3000)

    reload: () =>
        @discussion_id
        $.getJSON('/ajax/discuss/'+@discussion_id+'/messages',
            {_: new Date().getTime()},
            (data)->
                console.log(data)
        )


$ ->
    discuss = new Discuss($("#discussion_id").val())
    discuss.init()
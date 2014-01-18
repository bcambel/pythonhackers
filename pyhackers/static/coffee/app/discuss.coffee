
class @Discuss

    constructor: (@discussion_id) ->
        @lastMessage = null
        console.log "Discussion started #{@discussion_id}"

    init: () =>
        window.setInterval(@reload, 3000)

    reload: () =>
        @discussion_id
        $.getJSON('/ajax/discuss/'+@discussion_id+'/messages',
            {_: new Date().getTime(), after_id: @lastMessage or -1},
            (data) =>
                console.log(data)

                @lastMessage = data.discussion.last_message
        )


$ ->
    discuss = new Discuss($("#discussion_id").val())
    discuss.init()
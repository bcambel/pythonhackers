
class User
    postTemplate : window.Handlebars.compile($.trim($("#message-template").html()))
    projectTemplate: window.Handlebars.compile($.trim($("#project-template").html()))
    discussionTemplate: window.Handlebars.compile($.trim($("#discussion-template").html()))

    constructor : (@user_nick, @activeModule) ->
        console.log "Initialized"


    init : () ->
        $('a[data-toggle="tab"]').on('shown.bs.tab', (e) =>
          targetTab = $(e.target).attr("href")
          @loadModule(targetTab, e)
          # e.relatedTarget # previous tab
        )
        console.log "Initialized"

        @loadModule(@activeModule)

    loadModule: (target, evt) ->
        $tab = $('#user-tab')
        switch target
            when "#projects", "projects"
                if !evt?
                  $('#projects').addClass("active").siblings().removeClass("active")
                  $tab.find('a[href="#projects"]').parent().addClass("active").siblings().removeClass("active")
                do @loadProjects
            when "#timeline-container", "timeline"
                do @loadTimeline
            when "#discussions-container", "discussions"
                if !evt?
                  $('#discussions-container').addClass("active").siblings().removeClass("active")
                  $tab.find('a[href="#discussions-container"]').parent().addClass("active").siblings().removeClass("active")
                do @loadDiscussions
            else
                console.log "#{target} not found"

    loadProjects: () ->
        $projects = $("#projects")


        $.getJSON("/ajax/user/#{@user_nick}/projects",
            {_: new Date().getTime()},
            (data) =>
#                console.log(data)
                $projects.html(@projectTemplate(
                    projects: data.projects
                ))
        )

    loadTimeline: () ->
        $timeline = $("#timeline")


        $.getJSON("/ajax/user/#{@user_nick}/timeline",
            {_: new Date().getTime(), after_id: @lastMessage or -1},
            (data) =>
#                console.log(data)
                current_user_id = if PythonHackers.session then PythonHackers.session.id else -1

                _.each data.timeline, (p) ->
                    p.can_delete = p.user.id == current_user_id
                    p.display_context = if p.discussion_id is not null or p.discussion_id != "" then true else false

                $timeline.html(@postTemplate(
                    message: data.timeline
                ))
                @hideShowTrick()
        )

    hideShowTrick: () =>

        $("[data-message-id]").on("mouseenter", () ->
            $(this).find(".panel-footer").removeClass("hidden")
        ).on("mouseleave", () ->
            $(this).find(".panel-footer").addClass("hidden")
        )

    loadDiscussions: () ->
        $discussions= $("#discussions")
        $.getJSON("/ajax/user/#{@user_nick}/discussions",
            {_: new Date().getTime(), after_id: @lastMessage or -1},
            (data) =>
                console.log(data)
                _.each(data.discussions, (dd) ->
                    dd.user = data.user
                )
                $discussions.html(@discussionTemplate(
                    discussions: data.discussions
                ))
        )
$ ->
    user_nick = $("#user_nick").val()
    activeModule = $("#active_module").val()
    user = new User(user_nick, activeModule)
    user.init()




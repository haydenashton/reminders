<%inherit file="template.mak"/>
<%block name="content">
    <div class="container-fluid">
        <div class="well login-form">
            <form action="${url}" method="post">
                <input type="hidden" name="came_from" value="${came_from}"/>

                <div class="form-group">
                    <label>Email:</label>
                    <input type="text" class="form-control input input-large" name="email" value="${email}"/>
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" class="form-control input input-large" name="password" value="${password}"/><br/>
                </div>
                <input type="submit" class="btn btn-large btn-primary" name="form.submitted" value="Log In"/>
            </form>
        </div>
    </div>
</%block>


<%block name="app_includes">
    <link rel="stylesheet" href="${request.static_url('reminder:static/css/style.css')}"/>
</%block>
class ApiSchema:
    @staticmethod
    def url_for_owner_projects(host, project_data):
        return host + '/api/v1/projects/' + project_data["owner"] + "/"

    @staticmethod
    def url_for_pipelines(host, merkelypipe_data):
        return ApiSchema.url_for_owner_projects(host, merkelypipe_data)

    @staticmethod
    def url_for_project(host, project_data):
        return ApiSchema.url_for_owner_projects(host, project_data) + project_data["name"]

    @staticmethod
    def url_for_commit(host, project_data, commit):
        return ApiSchema.url_for_project(host, project_data) + '/commits/' + commit

    @staticmethod
    def url_for_artifacts(host, project_data):
        return ApiSchema.url_for_project(host, project_data) + '/artifacts/'

    @staticmethod
    def url_for_artifact(host, project_data, sha256_digest):
        return ApiSchema.url_for_artifacts(host, project_data) + sha256_digest

    @staticmethod
    def url_for_artifact_approvals(host, project_data, sha256_digest):
        return ApiSchema.url_for_artifact(host, project_data, sha256_digest) + '/approvals/'

    @staticmethod
    def url_for_releases(host, project_data):
        return ApiSchema.url_for_project(host, project_data) + '/releases/'

    @staticmethod
    def url_for_release(host, project_data, release_number):
        return ApiSchema.url_for_releases(host, project_data) + release_number

    @staticmethod
    def url_for_approvals(host, project_data):
        return ApiSchema.url_for_project(host, project_data) + '/approvals/'

    @staticmethod
    def url_for_approval(host, project_data, approval_number):
        return ApiSchema.url_for_approvals(host, project_data) + approval_number

    @staticmethod
    def url_for_deployments(host, project_data):
        return ApiSchema.url_for_project(host, project_data) + '/deployments/'

    @staticmethod
    def url_for_approvals(host, project_data):
        return ApiSchema.url_for_project(host, project_data) + '/approvals/'

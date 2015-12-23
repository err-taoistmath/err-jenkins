#!/usr/bin/python
import ast
from jenkins import Jenkins
from errbot import botcmd, BotPlugin
from config import JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD

__author__ = 'taoistmath'

class JenkinsBot(BotPlugin):

    def connect_to_jenkins(self):
        self.jenkins = Jenkins(JENKINS_URL, username=JENKINS_USERNAME, password=JENKINS_PASSWORD)

    @botcmd
    def jenkins_list(self, mess, args):
        """List all jobs, optionally filter them using a search term."""
        self.connect_to_jenkins()

        search_term = args.strip().lower()
        jobs = self.search_job(search_term)
        
        return self.format_jobs(jobs)


    @botcmd
    def jenkins_running(self, mess, args):
        """List all running jobs."""
        self.connect_to_jenkins()

        jobs = [job for job in self.jenkins.get_jobs() if 'anime' in job['color']]

        return self.format_running_jobs(jobs)


    @botcmd
    def jenkins_param(self, mess, args):
        """List Parameters for a given job."""
        self.connect_to_jenkins()
        
        if len(args) == 0:
            return u'What Job would you like the parameters for?'
        if len(args.split()) > 1:
            return u'Please enter only one Job Name'

        job_param = self.jenkins.get_job_info(args)['actions'][0]['parameterDefinitions']

        return self.format_params(job_param)


    @botcmd(split_args_with=None)
    def jenkins_build(self, mess, args):
        """Build a Jenkins Job with the given parameters
        Example: !jenkins build test_project FOO:bar
        """
        self.connect_to_jenkins()

        if len(args) == 0:
            return u'What job would you like to build?'

        parameters = self.build_parameters(args[1:])
        self.jenkins.build_job(args[0], parameters)
        running_job = self.search_job(args[0])
        
        return 'Your job should begin shortly: {0}'.format(self.format_jobs(running_job))


    def search_job(self, search_term):
        return [job for job in self.jenkins.get_jobs() if search_term.lower() in job['name'].lower()]


    def format_jobs(self, jobs):
        if len(jobs) == 0:
            return u'No jobs found.'

        max_length = max([len(job['name']) for job in jobs])
        return '\n'.join(['%s (%s)' % (job['name'].ljust(max_length), job['url']) for job in jobs]).strip()


    def format_running_jobs(self, jobs):
        if len(jobs) == 0:
            return u'No running jobs.'

        jobs_info = [self.jenkins.get_job_info(job['name']) for job in jobs]
        return '\n\n'.join(['%s (%s)\n%s' % (job['name'], job['lastBuild']['url'], job['healthReport'][0]['description']) for job in jobs_info]).strip()


    def format_params(self, job):
        parameters = ''

        for param in range (0, len(job)):
            parameters = parameters + ("Type: {0}\nDescription: {1}\nDefault Value: {2}\nParameter Name: {3}\n_\n"
                .format(job[param]['type'], job[param]['description'], str(job[param]['defaultParameterValue']['value']), job[param]['name']))

        return parameters


    def build_parameters(self, params):
        if len(params) == 0:
            return ast.literal_eval("{'':''}")

        parameters_list = "{'"

        for counter, param in enumerate(params):
            param = param.split(':')
            if counter < len(params) - 1:
                parameters_list = parameters_list + param[0].upper() + "': '" + param[1] + "', '"
            else:
                parameters_list = parameters_list + param[0].upper() + "': '" + param[1] + "'"

        parameters_list = parameters_list + '}'

        return ast.literal_eval(parameters_list)

# TransIP Collection

[![CI](https://github.com/roaldnefs/ansible-collection-transip/workflows/CI/badge.svg?event=push)](https://github.com/roaldnefs/ansible-collection-transip/actions)

This collection contains modules and plugins to assist in automating [TransIP][transip] infrastructure and API interactions with Ansible

## Tested with Ansible

Tested with the current Ansible 2.9 and 2.10 release and the current development version of Ansible. Ansible versions before 2.9.10 are not supported.

## Included content

- transip_sshkey – Manage TransIP SSH keys
- transip_vps – Create and delete a TransIP VPS

## Installation and Usage

### Installing the Collection from Ansible Galaxy

Before using the TransIP collection, you need to install it with the Ansible Galaxy CLI:

    ansible-galaxy collection install roaldnefs.transip

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yaml`, using the format:

```yaml
---
collections:
  - name: roaldnefs.transip
    version: 0.1.1
```

### Using modules from the TransIP Collection in your playbooks

It's preferable to use content in this collection using their Fully Qualified Collection Namespace (FQCN), for example: `roaldnefs.transip.transip_vps`:

```yaml
---
- hosts: localhost
  gather_facts: false
  connection: local

  task:
    - name: Create a new VPS
      roaldnefs.transip.transip_vps:
        state: present
        description: "example vps description"
        unique_description: yes
        product_name: vps-bladevps-x1
        operating_system: ubuntu-18.04
        access_token: REDACTED
      register: result
```

## Testing and Development

If you want to develop new content for this collection or improve what's already here, the easiest way to work on the collection is to clone it into one of the configured [`COLLECTIONS_PATHS`][ansible-collections-paths], ans work on it there.

## Testing with `ansible-test`

The `tests` directory contains configuration for running sanity and integeration tests using [`ansible-test`][ansible-test].

You can run the collection's test suites with the commands:

    ansible-test sanity --docker -v --color
    ansible-test integration --docker -v --color

Note: To run integration tests, you must add an [`integration_config.yml`][ansible-integration-config] file with a valid TransIP API key (using variable `transip_api_key`).

## Release notes

See the [changelog][changelog].

## Release process

Releases are automatically built and pushed to Ansible Galaxy for any new tag. Before tagging a release, make sure to do the following:

1. Update `galaxy.yml` and this README's `requirements.yml` example with the new `version` for the collection.
1. Update the CHANGELOG:
    1. Make sure you you have [`antsibull-changelog`][antsibull-changelog] installed.
    1. Make sure there are fragments for all known changes in `changelogs/fragments`.
    1. Run `antsibull-changelog release`.
1. Commit the changes and create a PR with the changes. Wait for tests to pass, then merge it once they have.
1. Tag the version in Git and push to GitHub.

After the version is published, verify it exists on the [TransIP Collection Galaxy page][ansible-galaxy-transip].

## More information

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [COPYING](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.

[transip]: https://www.transip.eu/
[changelog]: https://github.com/roaldnefs/transip-ansible-collection/blob/main/CHANGELOG.rst
[ansible-collections-paths]: https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths
[ansible-test]: https://docs.ansible.com/ansible/latest/dev_guide/testing_integration.html
[ansible-integration-config]: https://docs.ansible.com/ansible/latest/dev_guide/testing_integration.html#integration-config-yml
[antsibull-changelog]: https://pypi.org/project/antsibull-changelog/
[ansible-galaxy-transip]: https://galaxy.ansible.com/roaldnefs/transip
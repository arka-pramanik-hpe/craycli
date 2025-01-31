import click
import requests
from cray.utils import print_table

@click.group()
def rrs():
    """Manage Rack Resource State (RRS)"""
    pass

@rrs.command()
@click.pass_context
def list(ctx):
    """List all nodes across racks"""
    client = ctx.obj['client']
    
    try:
        response = client.get('/zone')
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        click.echo(f"Error fetching rack resources: {str(e)}", err=True)
        ctx.exit(1)

    headers = ['Rack', 'Name', 'Status', 'Roles', 'Age', 'Version', 'CPU', 'Memory']
    rows = []

    for rack, nodes in data.items():
        for node in nodes:
            rows.append([
                rack,
                node['name'],
                node['status'],
                node.get('roles', 'None'),
                node['age'],
                node['version'],
                node['cpu'],
                node['memory']
            ])

    print_table(headers, rows)
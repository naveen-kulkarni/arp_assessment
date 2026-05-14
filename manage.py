"""Initialize and manage the ARP Assessment platform."""
import os
import sys
import click
from src.backend.database import init_db, SessionLocal
from src.backend.data_generator import generate_mock_data, clear_mock_data

@click.group()
def cli():
    """ARP Assessment Platform CLI."""
    pass


@cli.command()
def init():
    """Initialize the database."""
    click.echo("🗄️  Initializing database...")
    try:
        init_db()
        click.secho("✅ Database initialized successfully", fg="green")
    except Exception as e:
        click.secho(f"❌ Error: {e}", fg="red")
        sys.exit(1)


@cli.command()
def seed():
    """Seed database with mock data."""
    click.echo("🌱 Seeding database with mock data...")
    db = SessionLocal()
    try:
        generate_mock_data(db)
        click.secho("✅ Mock data generated successfully", fg="green")
    except Exception as e:
        click.secho(f"❌ Error: {e}", fg="red")
        sys.exit(1)
    finally:
        db.close()


@cli.command()
@click.confirmation_option(prompt='Are you sure you want to clear all data?')
def clear():
    """Clear all data from database."""
    click.echo("🗑️  Clearing all data...")
    db = SessionLocal()
    try:
        clear_mock_data(db)
        click.secho("✅ All data cleared successfully", fg="green")
    except Exception as e:
        click.secho(f"❌ Error: {e}", fg="red")
        sys.exit(1)
    finally:
        db.close()


@cli.command()
def reset():
    """Reset database (clear and reseed)."""
    click.echo("🔄 Resetting database...")
    db = SessionLocal()
    try:
        clear_mock_data(db)
        click.echo("  ✓ Data cleared")
        generate_mock_data(db)
        click.secho("✅ Database reset successfully", fg="green")
    except Exception as e:
        click.secho(f"❌ Error: {e}", fg="red")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    cli()

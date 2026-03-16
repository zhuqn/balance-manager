"""
CLI main module using Click.

Synchronous version for Python 3.6 compatibility.
"""

import sys
from datetime import datetime, date
from typing import Optional

try:
    import click
except ImportError:
    print("Error: click is required. Install with: pip install click")
    sys.exit(1)

# Add parent to path for imports
sys.path.insert(0, str(__file__).parent.parent)

from core.manager import BalanceManager
from core.models import BalanceStatus, PlatformBalance
from core.exceptions import ManualEntryRequired
from providers import (
    OpenRouterProvider,
    MiniMaxProvider,
    VolcengineProvider,
    BFLProvider,
    ManualProvider,
)
from storage import JSONStorage
from config import load_config, create_default_config, save_config


@click.group()
@click.version_option(version="1.0.0", prog_name="balance-manager")
def cli():
    """
    Balance Management System
    
    Manage and monitor balances across multiple AI/ML platforms.
    """
    pass


@cli.command()
@click.option('--platform', '-p', default=None, help='Check specific platform only')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def check(platform: Optional[str], as_json: bool):
    """Check balances for all configured platforms."""
    config = load_config()
    manager = BalanceManager(
        warning_threshold=config.thresholds.warning,
        critical_threshold=config.thresholds.critical,
    )
    
    register_providers(manager, config)
    
    try:
        if platform:
            balance = manager.check_balance(platform)
            if as_json:
                click.echo(balance.to_dict())
            else:
                print_balance(balance)
        else:
            summary = manager.check_and_summarize()
            if as_json:
                import json
                click.echo(json.dumps(summary.to_dict(), indent=2))
            else:
                print_summary(summary)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--platform', '-p', required=True, help='Platform to enter balance for')
@click.option('--balance', '-b', type=float, required=True, help='Balance amount')
@click.option('--currency', '-c', default='USD', help='Currency code')
def enter(platform: str, balance: float, currency: str):
    """Manually enter balance for a platform."""
    config = load_config()
    
    if platform not in config.platforms:
        click.echo(f"Error: Unknown platform '{platform}'", err=True)
        sys.exit(1)
    
    provider = ManualProvider(
        platform_name=platform,
        stored_balance=balance,
        currency=currency,
    )
    
    result = provider.set_balance(balance, currency)
    
    # Save to storage
    storage = JSONStorage(config.storage.path)
    storage.save_balances([result])
    
    click.echo(f"✓ Balance entered for {platform}: {balance} {currency}")


@cli.command()
@click.option('--format', '-f', 'output_format', type=click.Choice(['text', 'json', 'csv']), default='text')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def summary(output_format: str, output: Optional[str]):
    """Display balance summary."""
    config = load_config()
    storage = JSONStorage(config.storage.path)
    
    balances = storage.load_balances()
    
    if not balances:
        click.echo("No balance data found. Run 'check' first.")
        return
    
    manager = BalanceManager(
        warning_threshold=config.thresholds.warning,
        critical_threshold=config.thresholds.critical,
    )
    summary = manager.get_summary(balances)
    
    if output_format == 'json':
        import json
        content = json.dumps(summary.to_dict(), indent=2)
    elif output_format == 'csv':
        content = format_csv(summary)
    else:
        content = format_summary_text(summary)
    
    if output:
        with open(output, 'w') as f:
            f.write(content)
        click.echo(f"Summary written to {output}")
    else:
        click.echo(content)


@cli.command()
def init():
    """Initialize configuration file."""
    from config.settings import get_config_path
    config_path = get_config_path()
    
    if config_path.exists():
        click.confirm(f"Config file exists at {config_path}. Overwrite?", abort=True)
    
    config = create_default_config()
    save_config(config, str(config_path))
    
    click.echo(f"✓ Configuration created at {config_path}")
    click.echo("\nNext steps:")
    click.echo("1. Edit the config file to add your API keys")
    click.echo("2. Run 'balance-manager check' to verify")


@cli.command()
def config():
    """Show current configuration."""
    config = load_config()
    
    click.echo("=== Balance Manager Configuration ===\n")
    
    click.echo("Thresholds:")
    click.echo(f"  Warning:  {config.thresholds.warning}")
    click.echo(f"  Critical: {config.thresholds.critical}")
    
    click.echo(f"\nStorage: {config.storage.type} @ {config.storage.path}")
    
    click.echo("\nPlatforms:")
    for name, pconfig in config.platforms.items():
        status = "✓" if pconfig.enabled else "✗"
        method = pconfig.method
        has_key = "✓" if pconfig.api_key else "✗"
        click.echo(f"  [{status}] {name}: method={method}, api_key={has_key}")


def register_providers(manager: BalanceManager, config):
    """Register all configured providers with the manager."""
    
    for name, pconfig in config.platforms.items():
        if not pconfig.enabled:
            continue
        
        if pconfig.method == "manual":
            provider = ManualProvider(platform_name=name)
        else:
            if name == "openrouter":
                provider = OpenRouterProvider(api_key=pconfig.api_key)
            elif name == "minimax":
                provider = MiniMaxProvider(api_key=pconfig.api_key)
            elif name == "volcengine":
                provider = VolcengineProvider(api_key=pconfig.api_key)
            elif name == "bfl":
                provider = BFLProvider(api_key=pconfig.api_key)
            else:
                provider = ManualProvider(platform_name=name)
        
        manager.register_provider(provider, pconfig)


def print_balance(balance: PlatformBalance):
    """Print a single balance in human-readable format."""
    status_icons = {
        BalanceStatus.ACTIVE: "✓",
        BalanceStatus.WARNING: "⚠",
        BalanceStatus.CRITICAL: "🔴",
        BalanceStatus.ERROR: "✗",
        BalanceStatus.UNKNOWN: "?",
    }
    
    icon = status_icons.get(balance.status, "?")
    
    click.echo(f"\n{icon} {balance.platform.upper()}")
    click.echo(f"  Balance: {balance.balance:.2f} {balance.currency}")
    click.echo(f"  Status:  {balance.status.value}")
    if balance.usage_this_month > 0:
        click.echo(f"  Usage:   {balance.usage_this_month:.2f} this month")
    click.echo(f"  Updated: {balance.last_updated.strftime('%Y-%m-%d %H:%M')}")


def print_summary(summary):
    """Print summary in human-readable format."""
    click.echo("\n" + "=" * 50)
    click.echo("       BALANCE MANAGEMENT SUMMARY")
    click.echo("=" * 50)
    click.echo(f"Generated: {summary.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo()
    
    click.echo(f"Total Platforms: {summary.platform_count}")
    click.echo(f"  ✓ Active:    {summary.platforms_active}")
    click.echo(f"  ⚠ Warning:   {summary.platforms_warning}")
    click.echo(f"  🔴 Critical: {summary.platforms_critical}")
    click.echo(f"  ✗ Error:    {summary.platforms_error}")
    click.echo()
    
    click.echo("-" * 50)
    click.echo("PLATFORM DETAILS:")
    click.echo("-" * 50)
    
    for balance in summary.balances:
        print_balance(balance)
        click.echo()


def format_csv(summary) -> str:
    """Format summary as CSV."""
    lines = ["platform,balance,currency,status,updated"]
    for balance in summary.balances:
        lines.append(
            f"{balance.platform},{balance.balance},{balance.currency},"
            f"{balance.status.value},{balance.last_updated.isoformat()}"
        )
    return "\n".join(lines)


def format_summary_text(summary) -> str:
    """Format summary as text."""
    lines = [
        "=" * 50,
        "       BALANCE MANAGEMENT SUMMARY",
        "=" * 50,
        f"Generated: {summary.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Total Platforms: {summary.platform_count}",
        f"  Active:    {summary.platforms_active}",
        f"  Warning:   {summary.platforms_warning}",
        f"  Critical:  {summary.platforms_critical}",
        f"  Error:     {summary.platforms_error}",
        "",
    ]
    return "\n".join(lines)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

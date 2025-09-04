import time
import random
from typing import Optional

from deskapp import Module, callback, Keys

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except Exception:  # handled in module
    boto3 = None
    BotoCoreError = Exception
    ClientError = Exception

from ..config import load_config

EC2_ID = random.random()


class EC2(Module):
    name = "AWS EC2"

    def __init__(self, app):
        super().__init__(app, EC2_ID)
        self.index = 1
        self._last_refresh: float = 0.0
        self._refresh_interval: float = 3.0
        self._status_lines = ["Loading EC2 status..."]
        self._error: Optional[str] = None
        self._session = None
        self._client = None
        self._instance_id: Optional[str] = None
        self._region_name: Optional[str] = None
        self._init_aws()
        # Trigger initial fetch soon
        self._last_refresh = 0.0

    def _init_aws(self):
        cfg = load_config()
        self._instance_id = cfg.get("instance_id")
        self._region_name = cfg.get("region_name")

        if boto3 is None:
            self._error = "boto3 is not installed. Install project deps to use AWS."
            return

        try:
            if cfg.get("access_key_id") and cfg.get("secret_access_key"):
                self._session = boto3.Session(
                    aws_access_key_id=cfg.get("access_key_id"),
                    aws_secret_access_key=cfg.get("secret_access_key"),
                    aws_session_token=cfg.get("session_token"),
                    region_name=self._region_name,
                )
            elif cfg.get("profile_name"):
                self._session = boto3.Session(
                    profile_name=cfg.get("profile_name"),
                    region_name=self._region_name,
                )
            else:
                # Default chain (env, IAM role, etc.)
                self._session = boto3.Session(region_name=self._region_name)

            self._client = self._session.client("ec2")
        except Exception as e:
            self._error = f"AWS init error: {e}"

    def _fetch_status(self):
        if not self._client or not self._instance_id:
            missing = []
            if not self._client:
                missing.append("AWS client")
            if not self._instance_id:
                missing.append("instance_id in config")
            self._status_lines = [
                "Cannot fetch EC2 status.",
                f"Missing: {', '.join(missing)}",
                "Configure ~/.config/deskapp/aws/config.toml",
            ]
            return

        try:
            resp = self._client.describe_instances(InstanceIds=[self._instance_id])
            rsv = resp.get("Reservations", [])
            if not rsv or not rsv[0].get("Instances"):
                self._status_lines = ["Instance not found or not visible."]
                return
            inst = rsv[0]["Instances"][0]
            state = inst.get("State", {}).get("Name", "unknown")
            inst_type = inst.get("InstanceType")
            az = inst.get("Placement", {}).get("AvailabilityZone")
            pub_ip = inst.get("PublicIpAddress")
            priv_ip = inst.get("PrivateIpAddress")

            self._status_lines = [
                f"Instance: {self._instance_id}",
                f"State   : {state}",
                f"Type    : {inst_type}",
                f"AZ      : {az}",
                f"Pub IP  : {pub_ip}",
                f"Priv IP : {priv_ip}",
            ]
        except (BotoCoreError, ClientError) as e:
            self._status_lines = [f"Error fetching status: {e}"]
        except Exception as e:
            self._status_lines = [f"Unexpected error: {e}"]

    def _maybe_refresh(self):
        now = time.time()
        if now - self._last_refresh >= self._refresh_interval:
            self._fetch_status()
            self._last_refresh = now

    def page(self, panel):
        # header/content
        panel.win.addstr(1, 2, "AWS EC2 Control", self.front.color_yellow)
        panel.win.addstr(2, 2, "Keys: [F] Refresh  [S] Start  [X] Stop  [R] Reboot  [Q] Quit", self.front.color_green)
        if self._error:
            panel.win.addstr(4, 2, f"Error: {self._error}", self.front.color_red)
            return

        # periodic refresh
        self._maybe_refresh()

        # render status
        y = 4
        for line in self._status_lines:
            try:
                panel.win.addstr(y, 2, line, self.front.color_cyan)
            except Exception:
                pass
            y += 1

    def _op(self, action: str):
        if not self._client or not self._instance_id:
            self.print("AWS not configured. Check config and deps.")
            return
        try:
            if action == "start":
                self._client.start_instances(InstanceIds=[self._instance_id])
                self.print("Start requested.")
            elif action == "stop":
                self._client.stop_instances(InstanceIds=[self._instance_id])
                self.print("Stop requested.")
            elif action == "reboot":
                self._client.reboot_instances(InstanceIds=[self._instance_id])
                self.print("Reboot requested.")
            # Force immediate refresh next frame
            self._last_refresh = 0.0
        except (BotoCoreError, ClientError) as e:
            self.print(f"AWS error: {e}")
        except Exception as e:
            self.print(f"Unexpected error: {e}")

    @callback(EC2_ID, Keys.S)
    def on_S(self, *args, **kwargs):
        self._op("start")

    @callback(EC2_ID, Keys.X)
    def on_X(self, *args, **kwargs):
        self._op("stop")

    @callback(EC2_ID, Keys.R)
    def on_R(self, *args, **kwargs):
        self._op("reboot")

    @callback(EC2_ID, Keys.F)
    def on_F(self, *args, **kwargs):
        self._last_refresh = 0.0
        self.print("Refreshing status...")


#!/usr/bin/env python3
import glob
import os
import jinja2
import subprocess


CARGO_TOML_TEMPLATE = """
{#- I eat whitespace -#}

[package]
name = "{{ folder_name }}"
version = "0.1.1"
edition = "2021"
license = "Apache-2.0"
description = "Device crate for the Microchip {{ model_name }}, generated from its SVD file."
repository = "https://github.com/RavuAlHemio/rust-svd/tree/main/{{ folder_name }}"
readme = "README.md"
keywords = ["microchip", "sam", "saml21", "svd", "svd2rust"]

[features]
rt = ["cortex-m-rt/device"]

[dependencies]
cortex-m = { version = "0.7" }
cortex-m-rt = { version = "0.7", optional = true }
critical-section = { version = "1.0", optional = true }
vcell = { version = "0.1" }

{#- I eat whitespace -#}
"""

README_TEMPLATE = """
{#- I eat whitespace -#}

# Microchip {{ model_name }} device crate

Code generated using [`svd2rust`](https://docs.rs/svd2rust/) from the SVD file obtained from the _Microchip SAML21 Series Device Support_ pack version 3.6.105 from https://packs.download.microchip.com/

{#- I eat whitespace -#}
"""

BUILD_RS_TEMPLATE = """
{#- I eat whitespace -#}

use std::env;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
fn main() {
    if env::var_os("CARGO_FEATURE_RT").is_some() {
        let out = &PathBuf::from(env::var_os("OUT_DIR").unwrap());
        File::create(out.join("device.x"))
            .unwrap()
            .write_all(include_bytes!("device.x"))
            .unwrap();
        println!("cargo:rustc-link-search={}", out.display());
        println!("cargo:rerun-if-changed=device.x");
    }
    println!("cargo:rerun-if-changed=build.rs");
}

{#- I eat whitespace -#}
"""


FILES = [
    ("Cargo.toml", CARGO_TOML_TEMPLATE),
    ("README.md", README_TEMPLATE),
    ("build.rs", BUILD_RS_TEMPLATE),
]


def main():
    env = jinja2.Environment(
        autoescape=False,
        undefined=jinja2.StrictUndefined,
    )
    files = [
        (filename, env.from_string(template))
        for (filename, template) in FILES
    ]

    for subdir in glob.glob("atsaml21*"):
        if os.path.exists(os.path.join(subdir, "DONTTOUCHME")):
            continue

        for (filename, template) in files:
            rendered = template.render(
                folder_name=subdir,
                model_name=subdir.upper(),
            )
            with open(os.path.join(subdir, filename), "w", encoding="utf-8") as f:
                f.write(rendered)
                f.write("\n")

        subprocess.run(
            ["svd2rust", "-i", f"{subdir.upper()}.svd"],
            cwd=subdir,
            check=True,
        )
        subprocess.run(
            ["form", "-i", "lib.rs", "-o", "src"],
            cwd=subdir,
            check=True,
        )
        os.unlink(os.path.join(subdir, "lib.rs"))
        subprocess.run(
            ["cargo", "fmt"],
            cwd=subdir,
            check=True,
        )
        subprocess.run(
            ["cargo", "build", "--all-features", "--target", "thumbv6m-none-eabi"],
            cwd=subdir,
            check=True,
        )
        subprocess.run(
            ["cargo", "publish", "--allow-dirty", "--dry-run"],
            cwd=subdir,
            check=True,
        )


if __name__ == "__main__":
    main()

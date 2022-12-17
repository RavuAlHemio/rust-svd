# SVD-based device crates for ARM microcontrollers/processors

Each subdirectory contains a crate for a specific ARM microcontroller or processor.

Most crates have been generated as follows:

1. Obtain the SVD file from a vendor-specific source (should be documented in the `README.md` of the crate).

2. Convert to Rust code using `svd2rust -i DEVICE.svd` ([svd2rust docs](https://docs.rs/svd2rust/)).

3. Unroll using `form -i lib.rs -o src` ([form docs](https://docs.rs/form/)).

4. Craft a `Cargo.toml`.

5. Beautify using `cargo fmt`.

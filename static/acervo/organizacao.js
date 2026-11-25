document.addEventListener("change", (event) => {
    const seletor = event.target.closest(".seletor-organizacao select");
    if (seletor) {
        seletor.form.requestSubmit();
    }
});

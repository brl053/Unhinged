import('./bootstrap').then(({ mount }) => {
    const localRoot = document.getElementById('root');

    mount({
            mountPoint: localRoot!,
            mountOptions: {}
        })
})
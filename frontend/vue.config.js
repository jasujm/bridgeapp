// This is required because otherwise unit tests loading SCSS breaks
// Code snippet from: https://github.com/vuetifyjs/vue-cli-plugins/issues/101

module.exports = {
    chainWebpack: function(config) {
        if (process.env.NODE_ENV == "test") {
            const scssRule = config.module.rule("scss");
            scssRule.uses.clear();
            scssRule.use("null-loader").loader("null-loader");
        }
    },
};

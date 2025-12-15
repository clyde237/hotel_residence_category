/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.ResidenceAvailability = publicWidget.Widget.extend({
    selector: '.s_residence_categories',

    start: function () {
        this._super.apply(this, arguments);
        this._refreshAvailability();
        // Actualiser toutes les 30 secondes
        setInterval(this._refreshAvailability.bind(this), 30000);
    },

    _refreshAvailability: function () {
        const self = this;
        this.$('.card').each(function () {
            const categoryId = parseInt($(this).data('category-id'));
            if (categoryId) {
                self._rpc({
                    route: `/residence/category/${categoryId}/availability`,
                }).then(function (data) {
                    $(this).find('.availability-badge').text(data.availability_display);
                });
            }
        });
    },
});

export default publicWidget.registry.ResidenceAvailability;
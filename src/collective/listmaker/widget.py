from zope.interface import implements
from zope.schema import getFieldNamesInOrder
from zope.schema.interfaces import ValidationError, RequiredMissing
from zope.browserpage import ViewPageTemplateFile
from zope.i18n import translate

from zope.formlib.interfaces import IDisplayWidget, IInputWidget
from zope.formlib.interfaces import WidgetInputError, MissingInputError
from zope.formlib.widget import InputWidget
from zope.formlib.widget import BrowserWidget
from zope.formlib.utility import setUpWidgets
from zope.formlib.i18n import _
from zope.formlib.utility import _createWidget


class ListMakerWidget(BrowserWidget, InputWidget):
    implements(IInputWidget)

    template = ViewPageTemplateFile('listmakerwidget.pt')

    _type = tuple

    _addButtonLabel = None

    def __init__(self, context, field, request, jscript=True, **kw):
        super(ListMakerWidget, self).__init__(context, request)

        self.names = getFieldNamesInOrder(self.context.value_type.schema)

        # set up my subwidgets
        self.jscript = jscript

        # but first, handle foo_widget specs being passed in
        for k, v in kw.items():
            if k.endswith('_widget'):
                setattr(self, k, v)

        self._setUpEditWidgets()

    def __call__(self):
        self._update()
        return self.template()

    def _update(self):
        sequence = self._getRenderedValue()

        editrow = self.request.form.get(self.editbutton, None)
        if editrow:
            self.editrow = editrow = int(editrow)
            for f, v in zip(self.names, sequence[editrow]):
                self.getSubWidget(f).setRenderedValue(v)
        elif self.savebutton in self.request.form:
            editrow = int(self.request.form[self.editingfield])
            newval = self._getInputValueFromSubWidgets()
            sequence[editrow] = tuple(newval)
            self._clear()

        self.sequence = self._type(sequence)
        num_items = len(self.sequence)
        self.marker = self._getPresenceMarker(num_items)

    def isEditing(self):
        return self.request.form.get(self.editbutton, None) is not None

    @property
    def editbutton(self):
        return self.name + '.row-edit'

    @property
    def deletebutton(self):
        return self.name + '.row-delete'

    @property
    def editingfield(self):
        return self.name + '.editing'

    @property
    def countfield(self):
        return self.name + '.count'

    @property
    def savebutton(self):
        return self.name + '.save'

    @property
    def cancelbutton(self):
        return self.name + '.cancel'

    @property
    def addbutton(self):
        return self.name + '.add'

    def _setUpEditWidgets(self):
        setUpWidgets(self, self.context.value_type.schema, IInputWidget,
                    prefix=self.name, names=self.names,
                    context=self.context)

    def _clear(self):
        """Clear the edit widgets"""
        for f in self.names:
                self.getSubWidget(f).setRenderedValue(None)

    def table(self, type='display'):
        assert type in ('display', 'input')
        type = IDisplayWidget if type == 'display' else IInputWidget
        sequence = self.sequence
        result = []
        for i, values in enumerate(sequence):
            widgets = self._getRow(i, type)
            for widget, value in zip(widgets, values):
                widget.setRenderedValue(value)
            result.append(widgets)
        return result

    def getSubWidget(self, name):
        return getattr(self, '%s_widget' % name)

    def subwidgets(self):
        return [self.getSubWidget(name) for name in self.names]

    def getAddButtonLabel(self):
        if self._addButtonLabel is None:
            button_label = _('Add %s')
            button_label = translate(button_label, context=self.request,
                                     default=button_label)
            title = self.context.title or self.context.__name__
            title = translate(title, context=self.request, default=title)
            self._addButtonLabel = button_label % title
        return self._addButtonLabel
        
    def setAddButtonLabel(self, value):
        self._addButtonLabel = value

    addButtonLabel = property(getAddButtonLabel, setAddButtonLabel)

    def saveButtonLabel(self):
        return _(u'Save')

    def cancelButtonLabel(self):
        return _(u'Cancel')

    def hasInput(self):
        """Is there input data for the field

        Return ``True`` if there is data and ``False`` otherwise.
        """

        if self.countfield in self.request.form:
            return True

        for name in self.names:
            if self.getSubWidget(name).hasInput():
                return True

        return False

    def _getInputValueFromSubWidgets(self):
        value = []
        for name in self.names:
            try:
                value.append(self.getSubWidget(name).getInputValue())
            except WidgetInputError, error:
                import pdb;pdb.set_trace()
                self._error = WidgetInputError(
                    self.context.__name__, self.label, error)
                raise self._error
            except ValidationError, error:
                import pdb;pdb.set_trace()
                self._error = WidgetInputError(
                    self.context.__name__, self.label, error)
                raise self._error
        return value

    def _getInputValueFromTable(self):
        sequence = self._type(self._generateSequence())
        return sequence

    def _generateSequence(self):
        try:
            count = int(self.request.form[self.countfield])
        except ValueError:
            # could not convert to int; the input was not generated
            # from the widget as implemented here
            raise WidgetInputError(self.context.__name__, self.context.title)

        # pre-populate
        sequence = [None] * count

        for i in range(count):
            sequence[i] = tuple(self._getRowValue(i))

        if self.addbutton in self.request.form:
            try:
                values = [w.getInputValue() for w in self.subwidgets()]
                sequence.append(tuple(values))
                self._clear()
            except WidgetInputError, error:
                pass  # TODO: How can we tell the user about this?

        todel = self.request.form.get(self.deletebutton, None)
        if todel is not None:
            todel = int(todel)
            del sequence[todel]

        return sequence

    def _getRow(self, i, type=IInputWidget):
        widgets = []
        for name in self.names:
            field = self.context.value_type.schema[name]
            widget = _createWidget(self.context, field, type, self.request)
            widget.setPrefix('%s.%d' % (self.name, i))
            widgets.append(widget)
        return widgets

    def _getRowValue(self, i):
        widgets = self._getRow(i)
        value = []
        for widget in widgets:
            if widget.hasValidInput():
                try:
                    value.append(widget.getInputValue())
                except WidgetInputError, error:
                    self._error = error
                    raise self._error
        return value

    def _getRenderedValue(self):
        """Returns a sequence from the request or _data"""
        if self._renderedValueSet():
            if self._data is self.context.missing_value:
                sequence = []
            else:
                sequence = list(self._data)
        elif self.hasInput():
            sequence = self._generateSequence()
        elif self.context.default is not None:
            sequence = self.context.default
        else:
            sequence = []
        return sequence

    def _getPresenceMarker(self, count=0):
        return ('<input type="hidden" name="%s" value="%d" />'
                % (self.countfield, count))

    def getInputValue(self):
        if not self.hasInput():
            raise MissingInputError(self.context.__name__,
                                    self.context.title, None)

        sequence = []
        # only process subwidgets if add button has been pressed
        if self.addbutton in self.request.form:
            sequence.append(self._getInputValueFromSubWidgets())

        sequence.extend(self._getInputValueFromTable())

        if not sequence and self.context.required:
            self._error = MissingInputError(self.context.__name__,
                                        self.context.title,
                                        RequiredMissing(self.context.__name__))
            raise self._error

        return sequence

    def editLink(self, row):
        name = self.editbutton
        return ('<a href="#" row="%d" name="%s" value="%s" '
                'onclick="javascript:return false;">edit</a>' %
                (row, name, name))

    def deleteLink(self, row):
        name = '%s.row-delete' % self.name
        return ('<a href="#" row="%d" name="%s" value="%s" '
                'onclick="javascript:return false;">delete</a>' %
                (row, name, name))

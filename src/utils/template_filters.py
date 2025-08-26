import datetime

def register_filters(app):
    """Register custom template filters"""
    
    @app.template_filter('datetime')
    def format_datetime(timestamp):
        """Format timestamp as datetime string"""
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
    
    @app.template_filter('index')
    def index_filter(lst, item):
        """Get index of item in list"""
        try:
            return lst.index(item)
        except ValueError:
            return -1
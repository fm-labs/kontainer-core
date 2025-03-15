from flask import Flask, jsonify, request
import traceback


class ErrorMiddleware:
    def __init__(self, app):
        self.app = app
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
        self.app.register_error_handler(Exception, self.handle_exception)

    def before_request(self):
        """Run before every request."""
        pass  # You can add logging or request validation here

    def after_request(self, response):
        """Run after every request."""
        return response

    def handle_exception(self, error):
        """Catches all uncaught exceptions and returns a JSON response."""
        error_message = str(error)
        error_traceback = traceback.format_exc()

        # Log the error
        print(f"Unhandled Exception: {error_message}")
        print(error_traceback)

        response = {
            "success": False,
            "error": "Internal Server Error",
            "message": error_message,
            "path": request.path
        }
        return jsonify(response), 500  # Returns HTTP 500 Internal Server Error
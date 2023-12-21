# Function to log messages with colored output
function log_message() {
    local msg_type=$1
    local message=$2
    local color
    local no_color="\033[0m" # Reset to default terminal color

    # Check if only one argument is provided
    if [ $# -eq 1 ]; then
        message=$1
        color=$no_color  # Use default terminal color for unspecified message types
    else
        # Set color based on message type
        case $msg_type in
            INFO) color="\033[0;32m" ;;  # Green for INFO
            ERROR) color="\033[0;31m" ;; # Red for ERROR
            *) color=$no_color ;;        # Default terminal color
        esac
    fi

    echo -e "${color}$(date '+%Y-%m-%d %H:%M:%S'): $message${no_color}"
}

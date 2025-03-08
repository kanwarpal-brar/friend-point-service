#!/bin/bash
# Friendship API CLI Tool

# Check if API key is set in environment variable
if [ -z "$FRIENDSHIP_API_KEY" ]; then
  echo "Warning: FRIENDSHIP_API_KEY environment variable not set."
  echo "   Using default value. Set it with: export FRIENDSHIP_API_KEY=your_key"
  export FRIENDSHIP_API_KEY="change_me_in_production"
fi

# Set this to your domain or localhost:5000 for local testing
BASE_URL=${FRIENDSHIP_API_URL:-"https://friendship.kanwarpal.com"}
API_PREFIX="/api"

# Helper functions
function print_header() {
  echo -e "\033[1;36m$1\033[0m"
  echo -e "\033[0;90m$2\033[0m"
  echo
}

function check_jq() {
  if ! command -v jq &> /dev/null; then
    echo "jq is not installed. JSON output will not be formatted."
    echo "   Install jq for prettier output:"
    echo "   - macOS: brew install jq"
    echo "   - Ubuntu/Debian: sudo apt-get install jq"
    echo "   - CentOS/RHEL: sudo yum install jq"
    echo
    JQ_CMD="cat"
  else
    JQ_CMD="jq"
  fi
}

function generate_secure_key() {
  # Generate a secure 64-character API key
  local length=${1:-64}
  if command -v python3 &> /dev/null; then
    python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '-_') for _ in range($length)))"
  elif command -v openssl &> /dev/null; then
    openssl rand -base64 $(($length * 3/4)) | tr -dc 'a-zA-Z0-9-_' | head -c $length
  else
    echo "Error: Neither python3 nor openssl is available to generate a secure key"
    return 1
  fi
}

function make_request() {
  local method=$1
  local endpoint=$2
  local data=$3
  local response
  
  if [ "$method" == "GET" ]; then
    response=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}${API_PREFIX}${endpoint}" \
      -H "X-API-Key: ${FRIENDSHIP_API_KEY}")
  else
    # Ensure data is properly quoted and escape sequences are correct
    # Also add debugging to see what's being sent
    echo "Sending request to: ${BASE_URL}${API_PREFIX}${endpoint}"
    echo "Data payload: $data"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}${API_PREFIX}${endpoint}" \
      -H "X-API-Key: ${FRIENDSHIP_API_KEY}" \
      -H "Content-Type: application/json" \
      -d "$data")
  fi
  
  # Extract status code from the last line
  local status_code=$(echo "$response" | tail -n1)
  # Extract the actual response body (everything except the last line)
  local body=$(echo "$response" | sed '$d')
  
  if [[ $status_code -ge 200 && $status_code -lt 300 ]]; then
    # Check if response is valid JSON before passing to jq
    if echo "$body" | jq empty 2>/dev/null; then
      echo "$body" | $JQ_CMD
    else
      echo "Warning: Received non-JSON response:"
      echo "$body"
    fi
  else
    echo "Error: Request failed with status code $status_code"
    echo "$body"
    echo "Request details:"
    echo "  Method: $method"
    echo "  Endpoint: ${BASE_URL}${API_PREFIX}${endpoint}"
    if [ "$method" != "GET" ]; then
      echo "  Payload: $data"
    fi
  fi
}

# Main menu
function show_menu() {
  clear
  echo -e "\033[1;35m=== Friend Point Service CLI ===\033[0m"
  echo -e "\033[0;90mAPI Key: ${FRIENDSHIP_API_KEY}\033[0m"
  echo -e "\033[0;90mBase URL: ${BASE_URL}\033[0m"
  echo
  echo "Choose an option:"
  echo "1. List all friends"
  echo "2. Get friend details"
  echo "3. Record positive interaction"
  echo "4. Record negative interaction"
  echo "5. Configure settings"
  echo "6. Delete a friend"
  echo "0. Exit"
  echo
  read -p "Enter choice [0-6]: " choice
  
  case $choice in
    1) list_all_friends ;;
    2) get_friend_details ;;
    3) record_positive_interaction ;;
    4) record_negative_interaction ;;
    5) configure_settings ;;
    6) delete_friend ;;
    0) exit 0 ;;
    *) 
      echo "Invalid choice. Press Enter to continue..."
      read
      show_menu
      ;;
  esac
}

function list_all_friends() {
  print_header "LISTING ALL FRIENDS" "Retrieving a list of all friends and their statuses"
  make_request "GET" "/friends"
  echo
  read -p "Press Enter to return to main menu..."
  show_menu
}

function get_friend_details() {
  read -p "Enter friend's name: " name
  print_header "GETTING FRIEND DETAILS" "Retrieving detailed information about $name"
  make_request "GET" "/friends/$name"
  echo
  read -p "Press Enter to return to main menu..."
  show_menu
}

function record_positive_interaction() {
  read -p "Enter friend's name: " name
  read -p "Enter points (positive number): " points
  read -p "Enter message/reason: " message
  
  # Validate points
  if (( $(echo "$points <= 0" | bc -l) )); then
    echo "Points must be a positive number for positive interactions!"
    read -p "Press Enter to try again..."
    record_positive_interaction
    return
  fi
  
  print_header "RECORDING POSITIVE INTERACTION" "Adding $points points for $name: $message"
  
  # Make sure to properly escape the quotes in the JSON payload
  data=$(printf '{"name":"%s","points":%s,"message":"%s"}' \
    "$(echo "$name" | sed 's/"/\\"/g')" \
    "$points" \
    "$(echo "$message" | sed 's/"/\\"/g')")
  
  make_request "POST" "/friends/interaction" "$data"
  echo
  read -p "Press Enter to return to main menu..."
  show_menu
}

function record_negative_interaction() {
  read -p "Enter friend's name: " name
  read -p "Enter points (positive number, will be made negative): " points
  read -p "Enter message/reason: " message
  
  # Validate points
  if (( $(echo "$points <= 0" | bc -l) )); then
    echo "Please enter a positive number (it will be converted to negative)!"
    read -p "Press Enter to try again..."
    record_negative_interaction
    return
  fi
  
  # Convert to negative
  negative_points=$(echo "-1 * $points" | bc -l)
  
  print_header "RECORDING NEGATIVE INTERACTION" "Subtracting $points points for $name: $message"
  
  # Make sure to properly escape the quotes in the JSON payload
  data=$(printf '{"name":"%s","points":%s,"message":"%s"}' \
    "$(echo "$name" | sed 's/"/\\"/g')" \
    "$negative_points" \
    "$(echo "$message" | sed 's/"/\\"/g')")
  
  make_request "POST" "/friends/interaction" "$data"
  echo
  read -p "Press Enter to return to main menu..."
  show_menu
}

function delete_friend() {
  read -p "Enter friend's name: " name
  read -p "Are you sure you want to delete $name? This cannot be undone. (y/N): " confirm
  
  if [[ "$confirm" =~ ^[Yy]$ ]]; then
    print_header "DELETING FRIEND" "Removing $name from your friends list"
    make_request "DELETE" "/friends/$name"
  else
    echo "Friend deletion canceled."
  fi
  
  echo
  read -p "Press Enter to return to main menu..."
  show_menu
}

function configure_settings() {
  clear
  echo -e "\033[1;35m=== Configuration ===\033[0m"
  echo
  echo "Current settings:"
  echo "1. API Key: $FRIENDSHIP_API_KEY"
  echo "2. Base URL: $BASE_URL"
  echo "3. Generate new secure API key"
  echo "4. Return to main menu"
  echo
  read -p "Enter choice [1-4]: " config_choice
  
  case $config_choice in
    1)
      read -p "Enter new API key: " new_key
      export FRIENDSHIP_API_KEY="$new_key"
      echo "API key updated!"
      ;;
    2)
      read -p "Enter new base URL: " new_url
      export FRIENDSHIP_API_URL="$new_url"
      BASE_URL="$new_url"
      echo "Base URL updated!"
      ;;
    3)
      echo "Generating secure API key..."
      new_key=$(generate_secure_key 64)
      if [ $? -eq 0 ]; then
        export FRIENDSHIP_API_KEY="$new_key"
        echo -e "\033[1;32mNew API key generated and set:\033[0m"
        echo "$new_key"
        echo -e "\033[1;33mIMPORTANT: Save this key somewhere safe!\033[0m"
        echo "To make it permanent, add to your shell profile:"
        echo "export FRIENDSHIP_API_KEY=\"$new_key\""
        echo
        echo "Also update your Kubernetes secret with:"
        echo "kubectl -n friendship create secret generic friendship-api-secret \\"
        echo "  --from-literal=api-key=\"$new_key\" --dry-run=client -o yaml | \\"
        echo "  kubectl apply -f -"
      else
        echo "Failed to generate secure API key."
      fi
      ;;
    4)
      show_menu
      return
      ;;
    *)
      echo "Invalid choice."
      ;;
  esac
  
  read -p "Press Enter to continue..."
  configure_settings
}

# Show quick help for command line usage
function show_help() {
  echo -e "\033[1;35mFriend Point Service CLI\033[0m"
  echo "Usage: $0 [command] [options]"
  echo
  echo "Commands:"
  echo "  list                List all friends"
  echo "  get <name>          Get details about a specific friend"
  echo "  add <name> <points> <message>"
  echo "                      Add a positive interaction"
  echo "  subtract <name> <points> <message>"
  echo "                      Add a negative interaction"
  echo "  delete <name>       Delete a friend"
  echo "  interactive         Launch interactive menu (default)"
  echo "  generate-key        Generate a secure API key"
  echo
  echo "Environment variables:"
  echo "  FRIENDSHIP_API_KEY  Your API key"
  echo "  FRIENDSHIP_API_URL  Base URL of the API"
  echo
  echo "Examples:"
  echo "  $0 list"
  echo "  $0 get \"Alex\""
  echo "  $0 add \"Alex\" 0.5 \"Helped with moving\""
  echo "  $0 subtract \"Alex\" 0.2 \"Forgot dinner plans\""
  echo "  $0 delete \"Alex\""
  echo "  $0 generate-key"
  echo
}

# Check for jq
check_jq

# Command-line interface
if [ $# -gt 0 ]; then
  case $1 in
    list)
      make_request "GET" "/friends"
      ;;
    get)
      if [ -z "$2" ]; then
        echo "Error: Missing friend name"
        show_help
        exit 1
      fi
      make_request "GET" "/friends/$2"
      ;;
    add)
      if [ -z "$4" ]; then
        echo "Error: Missing required parameters"
        echo "Usage: $0 add <name> <points> <message>"
        exit 1
      fi
      # Use printf to properly format the JSON
      data=$(printf '{"name":"%s","points":%s,"message":"%s"}' \
        "$(echo "$2" | sed 's/"/\\"/g')" \
        "$3" \
        "$(echo "$4" | sed 's/"/\\"/g')")
      make_request "POST" "/friends/interaction" "$data"
      ;;
    subtract)
      if [ -z "$4" ]; then
        echo "Error: Missing required parameters"
        echo "Usage: $0 subtract <name> <points> <message>"
        exit 1
      fi
      negative_points=$(echo "-1 * $3" | bc -l)
      # Use printf to properly format the JSON
      data=$(printf '{"name":"%s","points":%s,"message":"%s"}' \
        "$(echo "$2" | sed 's/"/\\"/g')" \
        "$negative_points" \
        "$(echo "$4" | sed 's/"/\\"/g')")
      make_request "POST" "/friends/interaction" "$data"
      ;;
    delete)
      if [ -z "$2" ]; then
        echo "Error: Missing friend name"
        echo "Usage: $0 delete <name>"
        exit 1
      fi
      read -p "Are you sure you want to delete \"$2\"? This cannot be undone. (y/N): " confirm
      if [[ "$confirm" =~ ^[Yy]$ ]]; then
        make_request "DELETE" "/friends/$2"
      else
        echo "Friend deletion canceled."
      fi
      ;;
    help)
      show_help
      ;;
    interactive)
      show_menu
      ;;
    generate-key)
      key_length=${2:-64}
      new_key=$(generate_secure_key $key_length)
      if [ $? -eq 0 ]; then
        echo -e "\033[1;32mGenerated API key ($key_length characters):\033[0m"
        echo "$new_key"
        echo -e "\033[1;33mIMPORTANT: Save this key somewhere safe!\033[0m"
      else
        echo "Failed to generate secure API key."
        exit 1
      fi
      ;;
    *)
      echo "Unknown command: $1"
      show_help
      exit 1
      ;;
  esac
else
  # No arguments provided, show interactive menu
  show_menu
fi

##imports
require_relative "./readme_generator"
require_relative "./comment_generator"
require_relative "./cloud_scroll_generator"
require_relative "./octokit_client"
require_relative "./cloud_types"

class Runner
  ## constants
  MARKDOWN_PATH = 'README.md'
  REGEX_PATTERN = /\w[\w' !?#@+-.]+/
  PERSONAL_REGEX = /`\w[\w]+`/
  ADDWORD = 'add'
  SHUFFLECLOUD = 'shuffle'
  USER = 'trinib'

  def initialize(
    github_token:,
    issue_number:,
    issue_title:,
    repository: "trinib/trinib",
    user:,
    development: false
  )
    @github_token = github_token
    @repository = repository
    @issue_number = issue_number
    @issue_title = issue_title
    @user = user
    @development = development
  end

  def run
    split_input = @issue_title.split('|')
    command = split_input[1]
    word = split_input[2]

    acknowledge_issue

    if command == SHUFFLECLOUD && word.nil?
      generate_cloud
      message = "@#{@user} regenerated the Word Cloud"
    elsif command == ADDWORD
      word = add_to_wordlist(word)
      generate_cloud
      message = "@#{@user} added '#{word}' to the Word Cloud"
      octokit.add_label(label: CloudTypes::CLOUDLABELS.last)
    else
      comment = "Sorry, the command 'wordcloud|#{command}' is not valid. Please try 'wordcloud|add|your-word' or 'wordcloud|shuffle'"
      octokit.error_notification(reaction: 'confused', comment: comment)
    end

    write(message)

  rescue StandardError => e
    comment = "There seems to be an error. Sorry about that."
    octokit.error_notification(reaction: 'confused', comment: comment, error: e)
  end

  def new_cloud
    if @user == USER
      File.open('previous_clouds/previous_clouds.md', 'a') do |f|
        f.puts add_to_cloud_scroll
      end
      move_old_cloud
      create_new_cloud
      if @development
        File.write('comment.md', new_pr_comment)
      else
        octokit.add_comment(comment: new_pr_comment)
      end
    end

  rescue StandardError => e
    comment = "Automatic Pull Request Comment could not be executed"
    octokit.error_notification(reaction: 'confused', comment: comment, error: e)
  end

  private

  def move_old_cloud
    `mv wordcloud/wordcloud.png previous_clouds/#{CloudTypes::CLOUDLABELS[-2]}_cloud#{CloudTypes::CLOUDLABELS.size - 1}.png`
    `mv wordcloud/wordlist.txt previous_clouds/#{CloudTypes::CLOUDLABELS[-2]}_cloud#{CloudTypes::CLOUDLABELS.size - 1}.txt`
    `touch wordcloud/wordlist.txt`
    if @development
      puts "Add #{CloudTypes::CLOUDLABELS[-2]}"
    else
      `git add previous_clouds/`
      `git diff`
      `git config --global user.email "github-action-bot@example.com"`
      `git config --global user.name "github-actions[bot]"`
      `git commit -m "Move #{CloudTypes::CLOUDLABELS[-2]} cloud" -a || echo "No changes to commit"`
      `git push`
    end
  end

  def create_new_cloud
    new_words = octokit.get_pull_request.body.split.grep(PERSONAL_REGEX).join("\n")
    File.open('wordcloud/wordlist.txt', 'w') { |file| file.puts new_words }
    generate_cloud
    write("New '#{CloudTypes::CLOUDLABELS.last}' word cloud generated")
  end

  def add_to_wordlist(word)
    #Check valid word
    invalid_word_error if word.nil?
    if word[REGEX_PATTERN] != word
      if word[REGEX_PATTERN] == word[1..-2] && word[1..-2].length > 2 && word[0] == "<" && word[-1] == ">"
        word = word[1..-2].downcase
      else
        invalid_word_error
      end
    end

    # Check for spaces
    word = word.gsub("_", " ")
    # Add word to list
    File.open('wordcloud/wordlist.txt', 'a') do |f|
      f.puts word
    end
    word
  end

  def invalid_word_error
    # Invalid expression, did not pass regex
    comment = "Sorry, your word was not valid. Please use valid alphanueric characters, spaces, apostrophes or underscores only"
    octokit.error_notification(reaction: 'confused', comment: comment)
  end

  def generate_cloud
    # Create new word cloud
    result = system('sort -R wordcloud/wordlist.txt | wordcloud_cli --imagefile wordcloud/wordcloud.png --prefer_horizontal 0.5 --repeat --fontfile wordcloud/Montserrat-Bold.otf --background black --colormask images/colourMask.jpg --width 700 --height 400 --regexp "\w[\w\' !?#@+-.]+" --no_collocations --min_font_size 10 --max_font_size 120')
    # Failed cloud generation
    unless result
      comment = "Sorry, something went wrong... the word cloud did not update :("
      octokit.error_notification(reaction: 'confused', comment: comment)
    end
    result
  end

  def write(message)
    File.write(MARKDOWN_PATH, to_markdown)
    if @development
      puts message
    else
      `git add README.md wordcloud/wordcloud.png wordcloud/wordlist.txt`
      `git diff`
      `git config --global user.email "github-action-bot@example.com"`
      `git config --global user.name "github-actions[bot]"`
      `git commit -m "#{message}" -a || echo "No changes to commit"`
      `git push`
      octokit.add_reaction(reaction: 'rocket')
    end
  end

  def to_markdown
    ReadmeGenerator.new(octokit: octokit).generate
  end

  def new_pr_comment
    CommentGenerator.new(octokit: octokit).generate
  end

  def add_to_cloud_scroll
    CloudScrollGenerator.new(octokit: octokit).generate
  end

  def acknowledge_issue
    octokit.add_label(label: 'wordcloud')
    octokit.add_reaction(reaction: 'eyes')
    octokit.close_issue
  end

  def raw_markdown_data
    @raw_markdown_data ||= octokit.fetch_from_repo(MARKDOWN_PATH)
  end

  def octokit
    @octokit ||= OctokitClient.new(github_token: @github_token, repository: @repository, issue_number: @issue_number)
  end
end

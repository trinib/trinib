require_relative "./cloud_types"

class CommentGenerator
  NEW_CLOUD_URL = "https://raw.githubusercontent.com/trinib/trinib/main/previous_clouds/#{CloudTypes::CLOUDLABELS[-2]}_cloud#{CloudTypes::CLOUDLABELS.size - 1}.png"
  ADDWORD = 'add'
  SHUFFLECLOUD = 'shuffle'
  WORDS_INITALIZED = 3

  def initialize(octokit:)
    @octokit = octokit
  end

  def generate
    current_contributors = Hash.new(0)
    current_words_added = WORDS_INITALIZED

    octokit.issues.each do |issue|
      if issue.title.split('|')[1] != SHUFFLECLOUD && issue.labels.any? { |label| label.name == CloudTypes::CLOUDLABELS[-2] }
        current_words_added += 1
        current_contributors[issue.user.login] += 1
      end
    end

    markdown = <<~HTML

    ## :cloud: :pencil2: Thanks for participating in our latest community word cloud!
    **:star2: Enjoyed yourself? [Add a word](https://github.com/trinib) to the NEW word cloud :fire:**

    ![Word Cloud Words Badge](https://img.shields.io/badge/Words%20in%20#{CloudTypes::CLOUDLABELS[-2]}%20cloud-#{current_words_added}-informational?labelColor=7D898B)
    ![Word Cloud Contributors Badge](https://img.shields.io/badge/Contributors%20in%20#{CloudTypes::CLOUDLABELS[-2]}%20cloud-#{current_contributors.size}-blueviolet?labelColor=7D898B)

    :tada: Check out the final product :tada:

    <div align="center">

      ## #{CloudTypes::CLOUDPROMPTS[-2]}

      <img src="#{NEW_CLOUD_URL}" alt="WordCloud" width="100%">
    </div>

    ### Thanks to everyone who added a word to the cloud

    HTML

    current_contributors.each do |username, count|
      markdown.concat("@#{username}\n")
    end

    markdown

  end

  private

  attr_reader :octokit

end
